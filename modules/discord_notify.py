import requests


def send_report_to_discord(bot_token, channel_id, applicant_name, applicant_email,
                             company_name, company_website, pdf_path):
    """Send report details + PDF attachment to a Discord channel via bot API."""
    if not bot_token or not channel_id:
        return {"success": False, "error": "Missing bot token or channel ID"}

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {bot_token}"}

    content = (
        f"**📋 New Company Research Report**\n"
        f"**Applicant:** {applicant_name} ({applicant_email})\n"
        f"**Company:** {company_name}\n"
        f"**Website:** {company_website}"
    )

    try:
        with open(pdf_path, "rb") as f:
            files = {"file": ("company_report.pdf", f, "application/pdf")}
            data = {"content": content}
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
            response.raise_for_status()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}