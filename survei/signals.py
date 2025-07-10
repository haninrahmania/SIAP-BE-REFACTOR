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

from github import Github, GithubException

from .models import Survei

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
    items = parse_wilayah(wilayah)
    return { item['id'].split('.')[0] for item in items }

def update_province_counts(province_codes, delta):
    # ── Load province code→name map from your FE app’s provinces.json ──
    fe_root        = Path(settings.BASE_DIR).parent / 'siap-fe-refactor'
    provinces_path = fe_root / 'my-app' / 'public'/ 'data' / 'provinces.json'
    with open(provinces_path, encoding='utf-8') as f:
        provinces = json.load(f)
    province_map = { p['code']: p['name'] for p in provinces }

    # ── GitHub setup ──
    gh       = Github(settings.GITHUB_TOKEN)
    repo     = gh.get_repo(settings.GITHUB_REPO)
    csv_path = 'data.csv'   # adjust if your CSV lives elsewhere

    # ── Fetch or initialize CSV ──
    try:
        contents = repo.get_contents(csv_path)
        raw_csv  = base64.b64decode(contents.content).decode('utf-8')
    except GithubException as e:
        if e.status == 404:
            # first run: create CSV with headers name,value
            initial = "name,value\n"
            repo.create_file(csv_path,
                             "Create initial data.csv",
                             initial)
            contents = repo.get_contents(csv_path)
            raw_csv  = initial
        else:
            raise

    # ── Parse existing counts (handle old 'count' or new 'value') ──
    reader = csv.DictReader(io.StringIO(raw_csv))
    counts = {}
    for row in reader:
        name       = row.get('name')
        val_str    = row.get('value', row.get('count', '0'))
        counts[name] = int(val_str or 0)

    # ── Apply +1 or –1 per province name ──
    for code in province_codes:
        name = province_map.get(code)
        if not name:
            continue
        counts[name] = max(counts.get(name, 0) + delta, 0)

    # ── Rebuild CSV with only name,value ──
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(['name', 'value'])
    for name in sorted(counts):
        writer.writerow([name, counts[name]])
    new_csv = out.getvalue()

    # ── Push updated CSV ──
    action = 'Incremented' if delta > 0 else 'Decremented'
    repo.update_file(
        path=csv_path,
        message=f"{action} province counts for Survei",
        content=new_csv,
        sha=contents.sha
    )

@receiver(post_save, sender=Survei)
def on_survei_created(sender, instance, created, **kwargs):
    if not created:
        return
    codes = extract_province_codes(instance.wilayah_survei)
    update_province_counts(codes, delta=1)

@receiver(post_delete, sender=Survei)
def on_survei_deleted(sender, instance, **kwargs):
    codes = extract_province_codes(instance.wilayah_survei)
    update_province_counts(codes, delta=-1)
