import os, urllib.request, urllib.parse, datetime
import requests
from io import BytesIO
from PIL import Image
from utils.logger import logger

_IMG_HDR = {"User-Agent": "Mozilla/5.0 Chrome/124 Safari/537", "Accept": "image/*;q=0.8"}
_SKIP = ["icon", "flag", "map", "logo", "diagram", "svg", "symbol", "coat", "blank", "book",
         "cover", "notebook", "paper", "text", "stamp", "chart", "drawing", "illustration",
         "clipart", "cartoon", "pattern", "background", "wallpaper", "texture", "sample",
         "template", "placeholder", "generic", "default", "unknown", "wiki", "commons"]
_EXTS = (".jpg", ".jpeg", ".png", ".webp")

def _get_img(url):
    try:
        r = requests.get(url, headers=_IMG_HDR, timeout=10, verify=False, allow_redirects=True)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", "") and len(r.content) > 10000:
            return r.content
    except Exception as e:
        logger.debug(f"Failed to download image from {url}: {e}")
        pass
    return None

def _clean_url(url):
    u = url.lower()
    if not any(u.endswith(e) or (e + "?") in u for e in _EXTS): return False
    return not any(kw in u for kw in _SKIP)

def _wiki_infobox(crop_key, crop_data):
    title = crop_data["wiki_titles"].get(crop_key.lower())
    if not title: return None
    try:
        r = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&titles={title}"
                         "&prop=pageimages&pithumbsize=600&format=json&origin=*",
                         headers={"User-Agent": "AssamCropRecommender/4.0"}, timeout=10, verify=False)
        if r.status_code == 200:
            for page in r.json().get("query", {}).get("pages", {}).values():
                thumb = page.get("thumbnail", {}).get("source", "")
                if thumb:
                    img = _get_img(thumb)
                    if img: return img
    except Exception as e:
        logger.warning(f"Wikipedia infobox fetch failed for {crop_key}: {e}")
        pass
    return None

def _wiki_search(crop_name):
    q = urllib.parse.quote(f"{crop_name} crop plant field")
    try:
        r = requests.get(f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
                         f"&gsrnamespace=6&gsrsearch={q}&prop=imageinfo&iiprop=url&iiurlwidth=600"
                         "&format=json&origin=*&gsrlimit=25",
                         headers={"User-Agent": "AssamCropRecommender/4.0"}, timeout=10, verify=False)
        if r.status_code == 200:
            for page in r.json().get("query", {}).get("pages", {}).values():
                info = page.get("imageinfo", [{}])[0]
                thumb = info.get("thumburl") or info.get("url", "")
                if thumb and _clean_url(thumb):
                    img = _get_img(thumb)
                    if img: return img
    except Exception as e:
        logger.warning(f"Wikipedia search failed for {crop_name}: {e}")
        pass
    return None

def _placeholder(crop_name):
    from PIL import ImageDraw, ImageFont
    W, H = 800, 600
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        draw.line([(0, y), (W, y)], fill=(int(26 + (45 - 26) * t), int(71 + (106 - 71) * t), int(42 + (79 - 42) * t)))
    
    label = crop_name.replace("_", " ").title()
    initials = "".join(w[0].upper() for w in label.split()[:2])
    
    # Use project-local font if available
    font_path = "NotoSans-Regular.ttf"
    try:
        if os.path.exists(font_path):
            fb = ImageFont.truetype(font_path, 80)
            fm = ImageFont.truetype(font_path, 52)
            fs = ImageFont.truetype(font_path, 24)
        else:
            fb = ImageFont.truetype("arial.ttf", 80)
            fm = ImageFont.truetype("arial.ttf", 52)
            fs = ImageFont.truetype("arial.ttf", 24)
    except:
        fb = fm = fs = ImageFont.load_default()
        
    draw.text((W // 2, H // 2 - 80), initials, font=fb, fill=(255, 255, 255, 30), anchor="mm")
    draw.text((W // 2, H // 2 + 20), label, font=fm, fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, H // 2 + 90), "No photo available", font=fs, fill=(180, 220, 180), anchor="mm")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def fetch_crop_image(crop_name, crop_data):
    key = crop_name.lower().replace(" ", "_")
    
    # 1. Check local images folder first
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        local_path = os.path.join("images", f"{key}{ext}")
        if os.path.exists(local_path):
            try:
                with open(local_path, "rb") as f:
                    logger.debug(f"Found local image for {crop_name}: {local_path}")
                    return f.read(), True
            except Exception as e:
                logger.warning(f"Error reading local image {local_path}: {e}")
                pass

    # 2. Fallback to Wikipedia
    logger.info(f"Local image not found for {crop_name}, fetching from Wikipedia...")
    img = _wiki_infobox(key, crop_data)
    if img: 
        logger.info(f"Found Wikipedia infobox image for {crop_name}")
        return img, True
        
    # NEW: Try search using the display name if the key/wiki_title fails
    display_name = crop_data.get("display_names", {}).get(key, crop_name)
    img = _wiki_search(display_name)
    if img: 
        logger.info(f"Found Wikipedia search image for {display_name}")
        return img, True
    
    # 3. Placeholder
    logger.info(f"No image found for {crop_name}, using placeholder.")
    return _placeholder(crop_name), False
