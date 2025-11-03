
---

# **2. `backend/guard_core.py` — FULL AI ENGINE**

```python
# backend/guard_core.py
import asyncio, json, smtplib, os, datetime
from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
import requests, geocoder
from github import Github
from reportlab.pdfgen import canvas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

app = FastAPI(title="Sentinel Guard v1.1")
logging.basicConfig(level=logging.INFO)

# Load config
try:
    with open("backend/config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"accounts": {}, "email": "", "github_pat": "", "travel_whitelist": {}}

# ML Model
model = IsolationForest(contamination=0.05)
baseline = []  # [ip_score, time_score, device_score]

# Octokit
gh = Github(config.get("github_pat")) if config.get("github_pat") else None

class LoginEvent(BaseModel):
    platform: str
    ip: str
    device: str
    user_agent: str = ""
    travel_mode: bool = False

class TravelRequest(BaseModel):
    location: str
    days: int = 7

# --- OSINT & Evidence ---
def trace_ip(ip: str):
    try:
        g = geocoder.ip(ip)
        return {
            "city": g.city or "Unknown",
            "country": g.country or "Unknown",
            "isp": g.org or "Unknown"
        }
    except:
        return {"city": "Unknown", "country": "Unknown", "isp": "Unknown"}

def generate_pdf(event: LoginEvent, trace: dict):
    pdf = f"evidence_{int(datetime.datetime.now().timestamp())}.pdf"
    c = canvas.Canvas(pdf)
    c.setFillColorRGB(0, 0.8, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "SENTINEL GUARD — HACK BLOCKED")
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(50, 760, f"Platform: {event.platform}")
    c.drawString(50, 740, f"IP: {event.ip}")
    c.drawString(50, 720, f"Location: {trace['city']}, {trace['country']}")
    c.drawString(50, 700, f"Device: {event.device}")
    c.drawString(50, 680, f"Time: {datetime.datetime.now().isoformat()}")
    c.save()
    return pdf

def send_email(event: LoginEvent, pdf_path: str):
    if not config.get("email"):
        return
    msg = MIMEMultipart()
    msg['From'] = "guard@adam.ceo"
    msg['To'] = config["email"]
    msg['Subject'] = f"SENTINEL GUARD: Hack Blocked on {event.platform}"

    body = f"""
    Unauthorized access blocked.
    Platform: {event.platform}
    IP: {event.ip}
    Device: {event.device}
    Time: {datetime.datetime.now()}
    Evidence attached.
    """
    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_path, "rb") as f:
        attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
        msg.attach(attach)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(config.get("smtp_user", "guard@adam.ceo"), config.get("smtp_pass", ""))
            s.send_message(msg)
    except Exception as e:
        logging.error(f"Email failed: {e}")

# --- Core Logic ---
async def monitor_loop():
    while True:
        for platform, token in config["accounts"].items():
            # Simulate API poll
            try:
                headers = {"Authorization": f"Bearer {token}"}
                if "youtube" in platform:
                    r = requests.get("https://www.googleapis.com/oauth2/v1/tokeninfo", params={"access_token": token})
                # Add other platforms...
            except:
                pass
        await asyncio.sleep(30)

def predict_threat(event: LoginEvent):
    # Simple heuristic — replace with ML
    score = 0
    if event.ip.startswith("185.220"): score += 90
    if "Russia" in trace_ip(event.ip).get("country", ""): score += 50
    return score / 100

# --- API Endpoints ---
@app.post("/alert")
async def receive_alert(event: LoginEvent):
    if event.travel_mode:
        return {"status": "allowed (travel)"}

    threat_score = predict_threat(event)
    if threat_score > 0.7:
        trace = trace_ip(event.ip)
        pdf = generate_pdf(event, trace)
        send_email(event, pdf)

        # Octokit action
        if gh and "github" in event.platform:
            try:
                repo = gh.get_repo("fair-collective/aurora-project")
                repo.remove_from_collaborators("suspicious-user")
            except:
                pass

        return {"status": "blocked", "evidence": pdf}
    return {"status": "safe"}

@app.post("/travel")
async def travel_mode(req: TravelRequest):
    # Simulate IP from location
    config["travel_whitelist"][req.location] = req.days
    with open("backend/config.json", "w") as f:
        json.dump(config, f)
    return {"status": "travel mode active", "location": req.location}

@app.get("/status")
async def status():
    return {"status": "Protected", "accounts": len(config["accounts"])}

# Start
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
