# import ast
# import json
# import os
# import io
# import csv
# import base64
# from pathlib import Path

# from django.apps import apps
# from django.conf import settings
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver

# from github import Github, GithubException

# from .models import Survei

# # --- Current Peta Survei logic:
# # 1. Mapping setiap province ke kode wilayah
# # 2. Survey Counts by Province untuk menghitung jumlah survei per provinsi
# # 3. Push ke data.csv pada public github repo sebagai datasource setiap kali Add New Survey
# #    untuk meng-increment jumlah survei
# # 4. Peta akan ter-update shortly after (Datawrapper tidak mendukung instant live update)
# # Konteks: csv pada public github repo digunakan karena Datawrapper tidak mendukung
# #          penggunaan local endpoint, sehingga diperlukan datasource yang dapat diakses.
# #          Hal ini dapat dipermudah ketika nanti sudah melakukan deployment (memakai API SIAP saja).

# def parse_wilayah(w):
#     """
#     Accept either a Python-list string or an actual list of dicts,
#     return a list of dicts.
#     """
#     if isinstance(w, str):
#         try:
#             return ast.literal_eval(w)
#         except (ValueError, SyntaxError):
#             return json.loads(w)
#     elif isinstance(w, list):
#         return w
#     else:
#         raise TypeError(f"Unexpected wilayah_survei type: {type(w)}")

# def extract_province_codes(wilayah):
#     items = parse_wilayah(wilayah)
#     return { item['id'].split('.')[0] for item in items }

# def update_province_counts(province_codes, delta):
#     # ── Load province code→name map from your FE app’s provinces.json ──
#     fe_root        = Path(settings.BASE_DIR).parent / 'siap-fe-refactor'
#     provinces_path = fe_root / 'my-app' / 'public'/ 'data' / 'provinces.json'
#     with open(provinces_path, encoding='utf-8') as f:
#         provinces = json.load(f)
#     province_map = { p['code']: p['name'] for p in provinces }

#     # ── GitHub setup ──
#     gh       = Github(settings.GITHUB_TOKEN)
#     repo     = gh.get_repo(settings.GITHUB_REPO)
#     csv_path = 'data.csv'   # adjust if your CSV lives elsewhere

#     # ── Fetch or initialize CSV ──
#     try:
#         contents = repo.get_contents(csv_path)
#         raw_csv  = base64.b64decode(contents.content).decode('utf-8')
#     except GithubException as e:
#         if e.status == 404:
#             # first run: create CSV with headers name,value
#             initial = "name,value\n"
#             repo.create_file(csv_path,
#                              "Create initial data.csv",
#                              initial)
#             contents = repo.get_contents(csv_path)
#             raw_csv  = initial
#         else:
#             raise

#     # ── Parse existing counts (handle old 'count' or new 'value') ──
#     reader = csv.DictReader(io.StringIO(raw_csv))
#     counts = {}
#     for row in reader:
#         name       = row.get('name')
#         val_str    = row.get('value', row.get('count', '0'))
#         counts[name] = int(val_str or 0)

#     # ── Apply +1 or –1 per province name ──
#     for code in province_codes:
#         name = province_map.get(code)
#         if not name:
#             continue
#         counts[name] = max(counts.get(name, 0) + delta, 0)

#     # ── Rebuild CSV with only name,value ──
#     out = io.StringIO()
#     writer = csv.writer(out)
#     writer.writerow(['name', 'value'])
#     for name in sorted(counts):
#         writer.writerow([name, counts[name]])
#     new_csv = out.getvalue()

#     # ── Push updated CSV ──
#     action = 'Incremented' if delta > 0 else 'Decremented'
#     repo.update_file(
#         path=csv_path,
#         message=f"{action} province counts for Survei",
#         content=new_csv,
#         sha=contents.sha
#     )

# @receiver(post_save, sender=Survei)
# def on_survei_created(sender, instance, created, **kwargs):
#     if not created:
#         return
#     codes = extract_province_codes(instance.wilayah_survei)
#     update_province_counts(codes, delta=1)

# @receiver(post_delete, sender=Survei)
# def on_survei_deleted(sender, instance, **kwargs):
#     codes = extract_province_codes(instance.wilayah_survei)
#     update_province_counts(codes, delta=-1)

import ast
import json
import os
import io
import csv
import base64
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from github import Github, GithubException

from .models import Survei

# --- Enhanced Peta Survei logic with ongoing surveys support:
# 1. Mapping setiap province ke kode wilayah
# 2. Survey Counts by Province untuk menghitung jumlah survei per provinsi
# 3. Support untuk both "all surveys" dan "ongoing surveys"
# 4. Push ke GitHub repo data.csv setiap kali ada perubahan survei
# 5. Peta akan ter-update shortly after (Datawrapper tidak mendukung instant live update)

def parse_wilayah(w):
    """
    Accept either a Python-list string or an actual list of dicts,
    return a list of dicts.
    """
    if isinstance(w, str):
        try:
            return ast.literal_eval(w)
        except (ValueError, SyntaxError):
            return json.loads(w)
    elif isinstance(w, list):
        return w
    else:
        raise TypeError(f"Unexpected wilayah_survei type: {type(w)}")

def extract_province_codes(wilayah):
    """Extract province codes from wilayah_survei data"""
    items = parse_wilayah(wilayah)
    return {item['id'].split('.')[0] for item in items}

def get_province_map():
    """Load province code→name mapping from frontend provinces.json"""
    fe_root = Path(settings.BASE_DIR).parent / 'siap-fe-refactor'
    provinces_path = fe_root / 'my-app' / 'public' / 'data' / 'provinces.json'
    
    try:
        with open(provinces_path, encoding='utf-8') as f:
            provinces = json.load(f)
        return {p['code']: p['name'] for p in provinces}
    except FileNotFoundError:
        # Fallback: create a basic province mapping if file not found
        print(f"Warning: provinces.json not found at {provinces_path}")
        return {}

def rebuild_all_province_counts():
    """
    Rebuild province counts from scratch by querying all existing surveys
    This ensures data consistency
    """
    from django.db.models import Q
    
    # Get province mapping
    province_map = get_province_map()
    if not province_map:
        print("Error: Could not load province mapping")
        return
    
    # Initialize counts
    all_counts = {}
    ongoing_counts = {}
    today = timezone.localtime(timezone.now()).date()
    
    # Query all surveys
    all_surveys = Survei.objects.all()
    
    for survey in all_surveys:
        if not survey.wilayah_survei:
            continue
            
        try:
            codes = extract_province_codes(survey.wilayah_survei)
            
            # Update counts for each province in this survey
            for code in codes:
                province_name = province_map.get(code)
                if not province_name:
                    continue
                
                # Count for all surveys
                all_counts[province_name] = all_counts.get(province_name, 0) + 1
                
                # Count for ongoing surveys only
                if (survey.tanggal_selesai and 
                    survey.tanggal_selesai > today):
                    ongoing_counts[province_name] = ongoing_counts.get(province_name, 0) + 1
                    
        except Exception as e:
            print(f"Error processing survey {survey.id}: {e}")
            continue
    
    # Update both CSV files
    update_github_csv(all_counts, csv_path='data.csv')
    update_github_csv(ongoing_counts, csv_path='data-ongoing.csv')

def update_github_csv(province_counts, csv_path='data.csv'):
    """
    Update the specified CSV file in GitHub with province counts
    """
    try:
        # GitHub setup
        gh = Github(settings.GITHUB_TOKEN)
        repo = gh.get_repo(settings.GITHUB_REPO)
        
        # Build CSV content
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(['name', 'value'])
        
        # Sort provinces and write data
        for name in sorted(province_counts.keys()):
            count = province_counts[name]
            if count > 0:  # Only include provinces with surveys
                writer.writerow([name, count])
        
        new_csv = out.getvalue()
        
        # Try to update existing file, or create if it doesn't exist
        try:
            contents = repo.get_contents(csv_path)
            repo.update_file(
                path=csv_path,
                message=f"Update {csv_path} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
                content=new_csv,
                sha=contents.sha
            )
            print(f"Successfully updated {csv_path}")
        except GithubException as e:
            if e.status == 404:
                # File doesn't exist, create it
                repo.create_file(
                    path=csv_path,
                    message=f"Create {csv_path}",
                    content=new_csv
                )
                print(f"Successfully created {csv_path}")
            else:
                raise
                
    except Exception as e:
        print(f"Error updating {csv_path}: {e}")

def update_province_counts_legacy(province_codes, delta):
    """
    Legacy method - kept for backward compatibility but not recommended
    Better to use rebuild_all_province_counts() for consistency
    """
    province_map = get_province_map()
    if not province_map:
        return

    # GitHub setup
    gh = Github(settings.GITHUB_TOKEN)
    repo = gh.get_repo(settings.GITHUB_REPO)
    csv_path = 'data.csv'

    # Fetch or initialize CSV
    try:
        contents = repo.get_contents(csv_path)
        raw_csv = base64.b64decode(contents.content).decode('utf-8')
    except GithubException as e:
        if e.status == 404:
            # First run: create CSV with headers name,value
            initial = "name,value\n"
            repo.create_file(csv_path,
                           "Create initial data.csv",
                           initial)
            contents = repo.get_contents(csv_path)
            raw_csv = initial
        else:
            raise

    # Parse existing counts
    reader = csv.DictReader(io.StringIO(raw_csv))
    counts = {}
    for row in reader:
        name = row.get('name')
        val_str = row.get('value', row.get('count', '0'))
        counts[name] = int(val_str or 0)

    # Apply delta per province name
    for code in province_codes:
        name = province_map.get(code)
        if not name:
            continue
        counts[name] = max(counts.get(name, 0) + delta, 0)

    # Rebuild CSV
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(['name', 'value'])
    for name in sorted(counts):
        if counts[name] > 0:  # Only include provinces with surveys
            writer.writerow([name, counts[name]])
    new_csv = out.getvalue()

    # Push updated CSV
    action = 'Incremented' if delta > 0 else 'Decremented'
    repo.update_file(
        path=csv_path,
        message=f"{action} province counts for Survei",
        content=new_csv,
        sha=contents.sha
    )

@receiver(post_save, sender=Survei)
def on_survei_created_or_updated(sender, instance, created, **kwargs):
    """
    Handle both creation and updates of surveys
    Rebuild from scratch to ensure consistency
    """
    try:
        print(f"Survey {'created' if created else 'updated'}: {instance.id}")
        rebuild_all_province_counts()
    except Exception as e:
        print(f"Error updating province counts after survey save: {e}")

@receiver(post_delete, sender=Survei)
def on_survei_deleted(sender, instance, **kwargs):
    """
    Handle survey deletion
    Rebuild from scratch to ensure consistency
    """
    try:
        print(f"Survey deleted: {instance.id}")
        rebuild_all_province_counts()
    except Exception as e:
        print(f"Error updating province counts after survey deletion: {e}")

# Manual trigger function for management commands
def manual_update_datawrapper_data():
    """
    Manually trigger data update for Datawrapper
    Can be called from management commands or admin
    """
    try:
        rebuild_all_province_counts()
        return True
    except Exception as e:
        print(f"Manual update failed: {e}")
        return False