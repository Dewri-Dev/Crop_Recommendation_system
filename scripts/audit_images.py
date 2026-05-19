
import os
import json
import requests
import time

def audit():
    with open("config/crop_data.json", "r", encoding="utf-8") as f:
        crop_data = json.load(f)

    crop_keys = crop_data.get("crop_keys", [])
    wiki_titles = crop_data.get("wiki_titles", {})
    
    local_images = os.listdir("images")
    local_keys = [os.path.splitext(f)[0] for f in local_images]

    missing_local = []
    missing_both = []
    found_wiki = []

    print(f"Auditing {len(crop_keys)} crops...\n")

    for key in crop_keys:
        # 1. Check local
        if key in local_keys:
            continue
        
        missing_local.append(key)
        
        # 2. Check Wikipedia
        title = wiki_titles.get(key)
        if not title:
            missing_both.append((key, "No wiki_title defined"))
            continue

        try:
            # Check Infobox
            r = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&titles={title}"
                             "&prop=pageimages&pithumbsize=100&format=json&origin=*",
                             headers={"User-Agent": "AssamCropAudit/1.0"}, timeout=5)
            
            thumb = None
            if r.status_code == 200:
                pages = r.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    thumb = page.get("thumbnail", {}).get("source")
                    if thumb: break
            
            if thumb:
                found_wiki.append(key)
            else:
                # NEW: Try search as a second chance
                display_name = crop_data.get("display_names", {}).get(key, key)
                q = requests.utils.quote(f"{display_name} crop plant field")
                r2 = requests.get(f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
                                 f"&gsrnamespace=6&gsrsearch={q}&prop=imageinfo&iiprop=url&iiurlwidth=100"
                                 "&format=json&origin=*",
                                 headers={"User-Agent": "AssamCropAudit/1.0"}, timeout=5)
                
                search_thumb = False
                if r2.status_code == 200:
                    pages2 = r2.json().get("query", {}).get("pages", {})
                    for p2 in pages2.values():
                        if p2.get("imageinfo"):
                            search_thumb = True
                            break
                
                if search_thumb:
                    found_wiki.append(key)
                else:
                    missing_both.append((key, f"Wiki page '{title}' and search both failed"))
            
            # Small delay to be polite
            time.sleep(0.1)
            
        except Exception as e:
            missing_both.append((key, f"Wiki API error: {e}"))

    print("-" * 40)
    print(f"SUMMARY:")
    print(f"Total Crops: {len(crop_keys)}")
    print(f"Local Images: {len(crop_keys) - len(missing_local)}")
    print(f"Wikipedia Fallbacks: {len(found_wiki)}")
    print(f"CRITICAL GAPS (No Local, No Wiki): {len(missing_both)}")
    print("-" * 40)
    
    if missing_both:
        print("\nCrops with NO image (Local or Wikipedia):")
        for key, reason in missing_both:
            print(f"- {key:20} | Reason: {reason}")
    else:
        print("\nAll crops have either a local image or a Wikipedia fallback!")

if __name__ == "__main__":
    audit()
