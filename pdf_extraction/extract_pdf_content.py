import pymupdf as fitz
import os
from PIL import Image
import io

def extract_pdf_content(pdf_path, output_folder):
    """
    Extract all text and images from a PDF file
    """
    # Create output directories
    text_folder = os.path.join(output_folder, "text")
    images_folder = os.path.join(output_folder, "images")
    os.makedirs(text_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)
    
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    all_text = []
    image_count = 0
    
    print(f"Processing PDF: {pdf_path}")
    print(f"Total pages: {len(doc)}")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Extract text
        text = page.get_text()
        all_text.append(f"=== PAGE {page_num + 1} ===\n{text}\n")
        
        # Save individual page text
        with open(os.path.join(text_folder, f"page_{page_num + 1}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        
        # Extract images
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            # Get image data
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            if pix.n < 5:  # GRAY or RGB
                img_data = pix.pil_tobytes(format="PNG")
                image_count += 1
                
                # Save image
                img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                img_path = os.path.join(images_folder, img_filename)
                
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)
                
                print(f"Extracted image: {img_filename}")
            
            pix = None
    
    # Save complete text
    complete_text_path = os.path.join(output_folder, "complete_text.txt")
    with open(complete_text_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    
    doc.close()
    
    print(f"Extraction complete!")
    print(f"Total images extracted: {image_count}")
    print(f"Text saved to: {complete_text_path}")
    print(f"Images saved to: {images_folder}")
    
    return complete_text_path, len(all_text), image_count

if __name__ == "__main__":
    # Process both PDF files
    pdf_files = ["../Assignment2 (5).pdf", "../Assignment2.pdf"]
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"\n{'='*50}")
            print(f"Processing: {pdf_file}")
            print(f"{'='*50}")
            
            # Create output folder for this PDF
            output_folder = os.path.join("pdf_extraction", pdf_file.replace(".pdf", "").replace(" ", "_").replace("(", "").replace(")", ""))
            
            try:
                extract_pdf_content(pdf_file, output_folder)
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
        else:
            print(f"PDF file not found: {pdf_file}")
