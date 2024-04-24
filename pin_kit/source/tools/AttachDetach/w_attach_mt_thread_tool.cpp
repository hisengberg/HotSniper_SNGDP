/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2016 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.  Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.  Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
/*! @file
 * This test checks:
 *  - Verify that all image load callbacks are being called before starting to Jit/Probe.
 *  - One of the threads that is created by application enter system call without leaving it (semaphore wait
 *    with no one releasing it). This test check that this kind of thread will not fail the test
 *    (for example, by stopping progress of Pin+Application in some way which shouldn't happen)
 */

#include <stdio.h>
#include <fstream>
#include "pin.H"
#include "tool_macros.h"
using namespace std;

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "callbacks_before_jit_or_probe_tool.out", "specify output file name");


ofstream TraceFile;
PIN_LOCK lock;

volatile BOOL jitOrProbeBegan = FALSE;

//==============================================================
//  Analysis Routines
//==============================================================

int PinAttached(unsigned int numOfThreads)
{
    jitOrProbeBegan = TRUE; // For probe mode
    TraceFile << "Replacement called." << endl;
    return 1;
}


//====================================================================
// Instrumentation Routines
//====================================================================

// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    jitOrProbeBegan = TRUE;
}

// This routine is executed for each image.
VOID ImageLoad(IMG img, VOID *)
{
    if ((IMG_Name(img).find("kernel.appcore.dll") != string::npos)
        || (IMG_Name(img).find("msvcrt.dll") != string::npos)
        || (IMG_Name(img).find("RPCRT4.dll") != string::npos))
    {   // Image that may be loaded after attach, ignoring it.
        return;
    }
    ASSERT(!jitOrProbeBegan, "Jit/Probe began before all image load callbacks were called. Image name: " + IMG_Name(img));

    if ( !IMG_IsMainExecutable(img) )
    {
        return;
    }

    RTN rtn = RTN_FindByName(img, C_MANGLE("PinIsAttached"));
    ASSERTX (RTN_Valid(rtn));
    TraceFile << "Replacing PinAttached" << endl;
    if (PIN_IsProbeMode())
    {
        ASSERTX(RTN_IsSafeForProbedReplacement(rtn));
        RTN_ReplaceProbed(rtn, AFUNPTR(PinAttached));
    }
    else
    {
        RTN_Replace(rtn, AFUNPTR(PinAttached));
    }
}

// This routine is executed once at the end.
VOID Fini(INT32 code, VOID *v)
{
    TraceFile.close();
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    PIN_ERROR(KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(INT32 argc, CHAR **argv)
{
    // Initialize the pin lock
    PIN_InitLock(&lock);

    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
    PIN_InitSymbols();

    TraceFile.open(KnobOutputFile.Value().c_str());

    if (!PIN_IsProbeMode())
    {
      // Register Instruction to be called to instrument instructions
      INS_AddInstrumentFunction(Instruction, 0);
    }

    // Register ImageLoad to be called when each image is loaded.
    IMG_AddInstrumentFunction(ImageLoad, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    if (PIN_IsProbeMode())
    {
        // Never returns
        PIN_StartProgramProbed();
    }
    else
    {
        // Never returns
        PIN_StartProgram();
    }

    return 0;
}
