import asyncio
from pyppeteer import launch

async def generate_pdf_from_html(html_content, pdf_path):
    browser = await launch()
    page = await browser.newPage()
    await page.setContent(html_content)
    await page.pdf({'path': pdf_path, 'format': 'A4'})
    await browser.close()

def html2pdf(html_content, output_path):
    if html_content.endswith(".html"):
        path = html_content
        with open(path) as f:
            html_content = f.read()
        if output_path is None:
            output_path = path.replace(".html", ".pdf")
    assert output_path is not None, "Failed to convert html to pdf. Please provide output_filename"
    asyncio.get_event_loop().run_until_complete(generate_pdf_from_html(html_content, output_path))


if __name__ == "__main__":
    path =  'summarization/results/summary_fixed.html'

    with open(path) as f:
        html_content = f.read()
    asyncio.get_event_loop().run_until_complete(generate_pdf_from_html(html_content, 'example2.pdf'))