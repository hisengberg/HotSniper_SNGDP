/*BEGIN_LEGAL 
BSD License 

Copyright (c) 2015 Intel Corporation. All rights reserved.
 
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

/*
 The LOOPPOINT class 
*/

#ifndef LOOPPOINT_H
#define LOOPPOINT_H

#include "dcfg_pin_api.H"
#include "pinplay.H"
#include "isimpoint_inst.H"

#include <iomanip>
#include <string>

#if !defined (TARGET_WINDOWS)
#  include <sys/cdefs.h>
#  if defined (PIN_CRT)
#    include <unordered_map>
#  else
#    include <tr1/unordered_map>
#  endif 
#else
#  include <unordered_map>
#endif

// We use unordered_map because it is more efficient than map for lookups.

using namespace std;
using namespace tr1;
using namespace dcfg_api;
using namespace dcfg_pin_api;

// buffer sizes.
#define DCFG_CACHELINE_SIZE 64

namespace looppoint {

            KNOB<string>knobDcfgFileName(KNOB_MODE_WRITEONCE,
                                         "pintool", "looppoint:dcfg-file", "",
                                         "Input this DCFG JSON file containing loop definitions"
                                         " and track loop statistics.");
            KNOB<UINT32>knobMaxThreads(KNOB_MODE_WRITEONCE,
                                "pintool", "looppoint:max_threads", "256",
                                  "Maximum number of threads supported (default 256).");

            // Maps to keep loop data by ID.
            typedef unordered_map<DCFG_ID, DCFG_ID_VECTOR> LoopBbsMap;

            struct LoopInfo {
                ADDRINT entryAddr;
            };

            typedef unordered_map<DCFG_ID, struct LoopInfo * > LoopInfoMap;

            class LOOPPOINT {

                // Highest thread id seen during runtime.
                UINT32 highestThreadId;

                // Data from DCFG.
                DCFG_DATA* dcfg;

                // Current process in DCFG.
                DCFG_PROCESS_CPTR curProc;

                // First BB executed.
                DCFG_BASIC_BLOCK_CPTR firstBb;

                // Currently active DCFG images.
                set<DCFG_ID> activeImageIds;

                LoopInfoMap loopInfoMap;

                ISIMPOINT *isimpointPtr;

            public:
                LOOPPOINT() : highestThreadId(0), dcfg(0), curProc(0), firstBb(0) {

                    // This assumes 'new' alignment is on a ptr-sized boundary so
                    // pointer will not be split across cache lines and each pointer
                    // will be on a separate cache line (pad may split cache lines,
                    // but that is ok).
                }

                // Return input string or 'unknown' if NULL, quoted.
                string safeStr(const string* str) const {
                    return string("\"") + (str ? *str : "unknown") + "\"";
                }

                // Find data from DCFG.
                void processDcfg() {
                    if (!dcfg)
                        return;

                    // Processes.
                    DCFG_ID_VECTOR processIds;
                    dcfg->get_process_ids(processIds);
                    if (processIds.size() != 1) {
                        cerr << "Error: DCFG file contains " << processIds.size() <<
                            " processes; expected exactly one." << endl;
                        exit(1);
                    }

                    // Get one and only process.
                    UINT32 pid = processIds[0];
                    curProc = dcfg->get_process_info(pid);
                    ASSERTX(curProc);

                    // process all loops.
                    DCFG_ID_VECTOR loopIds;
                    curProc->get_loop_ids(loopIds);
                    for (size_t li = 0; li < loopIds.size(); li++) {
                        DCFG_ID loopId = loopIds[li];
                        DCFG_LOOP_CPTR loop = curProc->get_loop_info(loopId);
                        ASSERTX(loop);
                        ASSERTX(loop->get_loop_id() == loopId);

                    }

                }

                // Process DCFG and add instrumentation.
                void activate(ISIMPOINT *isimpoint)
                {
                    isimpointPtr = isimpoint;
                    string dcfgFilename = knobDcfgFileName.Value();
                    if (dcfgFilename.length() == 0) {
                        //Not tracking loops because no DCFG input file given.
                        return;
                    }

                    // Make a new DCFG object.
                    dcfg = DCFG_DATA::new_dcfg();

                    // Read from file.
                    string errMsg;
                    if (!dcfg->read(dcfgFilename, errMsg)) {
                        cerr << "looppoint: " << errMsg <<
                            "; use " << knobDcfgFileName.Cmd() << endl;
                        exit(1);
                    }

                    // Get data from DCFG.
                    processDcfg();

                    // Add Pin instrumentation.
                    TRACE_AddInstrumentFunction(handleTrace, this);
                    IMG_AddInstrumentFunction(loadImage, this);
                    PIN_AddThreadStartFunction(ThreadStart, 0);
                    IMG_AddUnloadFunction(unloadImage, this);
                }
        


            // Analysis routine for the entry DCFG basic block for a loop
            static VOID 
            enterLoop( 
                ADDRINT insAddr,
                struct LoopInfo *li,
                LOOPPOINT *lt, 
                UINT32 imageId,
                THREADID tid) {

                if(lt->isimpointPtr->VectorPending(tid))
                {
                    // A slice ended in isimpoint but frequency vector
                    // was not emitted. Do it now.
                    // DCFG imageID starts from 1, isimpoint starts counting
                    // images from 0 hence passing 'imageId -1'
                    lt->isimpointPtr->EmitVectorForFriend(insAddr, imageId-1,
                        tid, lt->isimpointPtr);
                }
            }

            static VOID ThreadStart(THREADID threadid, CONTEXT *ctxt,
                 INT32 flags, VOID *v)
            {
                if(threadid==knobMaxThreads)
                {
                    cerr << "\tMaximum number of threads (" << 
                        knobMaxThreads << ") reached. \n\t Change with"
                          " -looppoint:max_threads NEWVAL." << endl; 
                    exit(1);
                }
            }

            // called when an image is loaded.
            static VOID loadImage(IMG img, VOID *v)
            {
                LOOPPOINT *lt = static_cast<LOOPPOINT *>(v);
                ASSERTX(lt);

                // Get Pin image data.
                UINT32 imgId = IMG_Id(img);

                // Get corresponding DCFG image data.
                DCFG_IMAGE_CPTR dcfgImage = lt->curProc->get_image_info(imgId);
                if (!dcfgImage) {
                    cerr << "Warning: image " << imgId 
                        << " is not in DCFG; ignoring." << endl;
                    return;
                }

                // Check for consistency.
            if (ADDRINT(dcfgImage->get_base_address()) != IMG_LowAddress(img)) 
            {
                cerr << "Warning: image " << imgId <<
                    " is not at DCFG reported address; ignoring." << endl;
                return;
            }

            // Remember.
            lt->activeImageIds.insert(imgId);
        }

        // called when an image is unloaded.
        static VOID unloadImage(IMG img, VOID *v)
        {
            LOOPPOINT *lt = static_cast<LOOPPOINT *>(v);
            ASSERTX(lt);
            UINT32 imgid = IMG_Id(img);
            lt->activeImageIds.insert(imgid);
            lt->activeImageIds.erase(imgid);
        }

        // Add analysis routines when a trace is delivered.
        static VOID handleTrace(TRACE trace, VOID *v)
        {
            LOOPPOINT *lt = static_cast<LOOPPOINT *>(v);
            ASSERTX(lt);

            // loop thru all BBLs in this trace.
            for(BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
            {
                // loop thru all the instrs in this BBL.
                for (INS ins = BBL_InsHead(bbl); INS_Valid(ins); ins = INS_Next(ins))
                {
                    ADDRINT insAddr = INS_Address(ins);

                    // Get DCFG BBs containing this address.
                    // There will usually be one 
                    //  (or zero if the BB was never executed).
                    // There might be more than one under certain 
                    // circumstances like
                    // image unload followed by another load.
                    DCFG_ID_VECTOR bbIds;
                    lt->curProc->get_basic_block_ids_by_addr(insAddr, bbIds);
                    for (size_t bbi = 0; bbi < bbIds.size(); bbi++) {
                        DCFG_ID bbId = bbIds[bbi];
                        DCFG_BASIC_BLOCK_CPTR bb = 
                            lt->curProc->get_basic_block_info(bbId);
                        ASSERTX(bb);
                        ASSERTX(bb->get_basic_block_id() == bbId);
                        UINT64 bbAddr = bb->get_first_instr_addr();

                        // We only want BBs in active images.
                        DCFG_ID imgId = bb->get_image_id();
                        if (!lt->activeImageIds.count(imgId)) {
                            // bb not in an active image. Skip.
                            continue;
                        }
                        DCFG_ID currentLoopId = bb->get_inner_loop_id();
                        // if bbId == currentLoopId, we have a loop-entry bb.
                        if((bbId == currentLoopId) && (insAddr == bbAddr))
                        {
                             LoopInfoMap::const_iterator lit = 
                                lt->loopInfoMap.find(currentLoopId);
                             struct LoopInfo *loopInfo = NULL;
                             if(lit == lt->loopInfoMap.end())
                             {
                                loopInfo = new (struct LoopInfo);

                                loopInfo->entryAddr = insAddr;
                            }
                            else
                            {
                                loopInfo = lit->second;
                            }
                            // first instruction of the loop entry bb
                            // bb is the loop head
                            INS_InsertCall(ins, IPOINT_BEFORE,
                                    (AFUNPTR)enterLoop,
                                    IARG_ADDRINT, insAddr, 
                                    IARG_PTR, loopInfo,
                                    IARG_PTR, lt,
                                    IARG_UINT32, imgId,
                                    IARG_THREAD_ID,
                                    IARG_END);
                        }
                    }
                } // INS.
            } // BBL.
        }
    };

} // namespace
#endif
