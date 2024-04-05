# A smallish script to generate previews of the content of a PDF file,
# as a stacked strip, running left to right, with the left-most one on top.

# Define the maximum number of images/pages to process
maximages=$1
output_file=$2

# set default if the output file not provided
if [ -z "$output_file" ]; then
    output_file="final_strip.png"
fi

# Convert all pages of the PDF into individual PNGs with added border.
convert -quality 100 -density 200 -colorspace sRGB \
    "export.pdf[0-$((maximages - 1))]" \
    -background white -alpha remove \
    -resize '600x600>' \
    -bordercolor Black -border 3 \
    page-%02d.png

# Get the number of images
image_files=(page-*.png)
N=${#image_files[@]}

# Distort all images
for file in "${image_files[@]}"; do
    # Add extra space on the right to accommodate the distortion.
    convert "$file" -matte -virtual-pixel transparent \
        -alpha set \
        -background none -splice 10x0 \
        -distort Perspective '0,0,60,45  600,0,600,0  600,600,600,600  0,600,60,570' \
        +repage "temp-$file"        
done

# Assume all images have the same dimensions as the first image
height=$(identify -format "%h" "${image_files[0]}")
width=$(identify -format "%w" "${image_files[0]}")

overlap=100

# Calculate total canvas width based on the number of images and the overlap
total_width=$(( (width - overlap) * (N - 1) + width))

# Create a transparent canvas
convert -size ${total_width}x${height} xc:transparent canvas.png

# Make sure we are using the sRGB color space
convert canvas.png -colorspace sRGB canvas.png

# Set the initial offset to be the width of one image minus the overlap
# This is where the rightmost image's left edge should be
offset=$((total_width - width - overlap/2))

# Composite images onto the canvas from right to left with the required overlap
for (( idx=N-1; idx>=0; idx-- )); do
  img=${image_files[idx]}
  convert canvas.png "temp-$img" -colorspace sRGB -geometry +${offset}+0 -composite canvas.png
  # Decrement the offset by (image width - overlap) for the next image to the left
  offset=$((offset - (width - overlap)))
done

# Rename the final image
mv canvas.png "$output_file"

# Clean up temporary images.
rm temp-*.png
rm page-*.png