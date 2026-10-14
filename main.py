from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import Response
import pikepdf
import io

app = FastAPI()

@app.post("/decrypt")
async def decrypt_pdf(
    password: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # 1. 讀取上傳的加密 PDF
        pdf_bytes = await file.read()
        
        # 2. 使用 pikepdf (底層為 qpdf) 透過密碼解開 PDF
        with pikepdf.open(io.BytesIO(pdf_bytes), password=password) as pdf:
            # 3. 將無密碼的 PDF 存入暫存記憶體
            output_buffer = io.BytesIO()
            pdf.save(output_buffer)
            
        # 4. 將脫密後的檔案回傳給 n8n
        return Response(
            content=output_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="decrypted_{file.filename}"'
            }
        )
        
    except pikepdf.PasswordError:
        raise HTTPException(status_code=401, detail="密碼錯誤，無法解密")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 處理失敗: {str(e)}")
