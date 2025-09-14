# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.ocr import extract_text_from_pdf
from app.parser import extract_with_llm, extract_fields_simple
from app.cleaner import normalize_claim
from app.judge import llm_judge, deterministic_checks
from app.reporter import make_report, report_to_markdown

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Claims Adjuster - MVP")

@app.post("/process-claim")
async def process_claim(file: UploadFile = File(...)):
    # accept PDFs or plain text
    data = await file.read()
    try:
        text = extract_text_from_pdf(data)
    except Exception as e:
        # fallback to raw text assuming plain text file
        try:
            text = data.decode("utf-8")
        except:
            raise HTTPException(status_code=400, detail=f"Could not read file: {e}")

    # first attempt quick heuristics
    parsed = extract_fields_simple(text)
    # then run LLM extraction for better coverage (non-blocking fallback)
    try:
        llm_parsed = extract_with_llm(text)
        # merge: prefer LLM fields when non-null
        for k, v in (llm_parsed or {}).items():
            if v is not None:
                parsed[k] = v
    except Exception as e:
        print("LLM parse failed:", e)

    claim = normalize_claim(parsed)
    # deterministic check
    det = deterministic_checks(claim)
    # LLM judge
    judge_res = llm_judge(claim)
    report = make_report(claim, judge_res)
    md = report_to_markdown(report)
    return JSONResponse({"claim": claim, "judge": judge_res, "report_markdown": md})
