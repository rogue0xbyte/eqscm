import pandas as pd
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image, ImageDraw, ImageFont

# Configuration
file_path = "TA 25 EG1ASP.xlsx"
output_directory = "./qrs-new/"
qr_code_size = (300, 300)  # Size for individual QR codes

def clean_row(row):
    """Filter out keys with invalid values (NaN, empty, etc.)."""
    return {k: v for k, v in row.items() if pd.notna(v) and v != '' and v != 'NULL' and v != 'NaN'}

def generate_qr_image(equipment_tag, job_id, wo_id, link):
    """Generate a QR code with Equipment TAG No., Job ID, and WO ID below, preserving full image size."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)
    
    # Generate QR code image
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=RadialGradiantColorMask(
            back_color=(255, 255, 255),
            center_color=(0, 0, 0),
            edge_color=(0, 0, 0)
        ),
        eye_drawer=GappedSquareModuleDrawer()
    ).convert("RGB")

    # Load and position the logo in the center of the QR code
    logo = Image.open("equate-logo-2.png").convert("RGBA")
    logo_size = (80, 80)
    logo = logo.resize(logo_size)

    # Calculate positioning for logo overlay
    img = img.convert("RGBA")
    img_w, img_h = img.size
    logo_w, logo_h = logo.size
    pos = ((img_w - logo_w) // 2, (img_h - logo_h) // 2)

    # Overlay the logo
    img.paste(logo, pos, logo)

    # Add Equipment TAG, Job ID, and WO ID below QR code without cropping
    draw = ImageDraw.Draw(img)
    
    font_size = 20  # Initial font size
    font = ImageFont.load_default(font_size)

    # Text to be added below the QR code
    equipment_text = f"TAG: {equipment_tag}"
    job_id_text = f"JOB ID: {job_id}"
    wo_id_text = f"WO: {wo_id}"

    # Combine the text lines into one string for easy bounding box calculation
    full_text = f"{equipment_text}\n{job_id_text}\n{wo_id_text}"

    # Use textbbox to calculate text dimensions
    text_bbox = draw.textbbox((0, 0), full_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]  # width of the text
    text_height = text_bbox[3] - text_bbox[1]  # height of the text
    
    # Create a new image to fit both QR code and text
    img_with_text = Image.new("RGB", (img.width, img.height + text_height + 10), "white")
    img_with_text.paste(img, (0, 0))  # Paste the original QR code

    # Draw the text below the QR code
    draw = ImageDraw.Draw(img_with_text)
    draw.text(((img.width - text_width) // 2, img.height - 2), full_text, fill="black", font=font)

    return img_with_text




def main():
    # Load Excel data
    df = pd.read_excel(file_path)

    # Iterate over rows
    for idx, row in df.iterrows():
        cleaned_data = clean_row(row.to_dict())

        # Skip if mandatory 'Equipment TAG No.' is missing
        equipment_tag = cleaned_data.get("Equipment TAG No")
        if not equipment_tag:
            print("Skipping row due to missing Equipment TAG No.")
            continue
        if equipment_tag in ["MXK-FV-6811-09", "MXK-FV-6851-05", "MXK-FV-6213-01", "MXK-HV-8300-39", "MXK-FV-6733-01",
                                "MXK-HV-6718-02", "MXK-PSV-6780-800R", "MXK-FV-6811-09"]:

            # Generate QR code image
            qr_image = generate_qr_image(equipment_tag, cleaned_data.get("Job ID"), cleaned_data.get("Work Order No"), f'https://eqscm.intellx.in/status/{cleaned_data.get("Equipment TAG No")}')

            # Save the QR code image
            qr_image.save(f"{output_directory}{equipment_tag}_qr.png")
            print(f"QR Code for {equipment_tag} saved.")

if __name__ == "__main__":
    main()
