import requests

url = "http://localhost:8000/api/v1/generate-roast"

# Download a real image
print("📥 Downloading test image...")
img_url = "https://picsum.photos/200/300"
img_data = requests.get(img_url).content
with open("test_image.jpg", "wb") as f:
    f.write(img_data)

files = {
    "image": ("test_image.jpg", open("test_image.jpg", "rb"), "image/jpeg")
}
data = {
    "name": "Test User",
    "taste": "Nickelback, Crocs, Marvel movies"
}

print("🚀 Sending request to API...")
try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.json())
except Exception as e:
    print(f"❌ Error: {e}")
