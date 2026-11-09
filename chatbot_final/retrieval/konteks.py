# ============================================================
# retrieval/konteks.py
# Penyusunan lembar contekan konteks untuk LLM dan format sumber.
# ============================================================

import json


def _label_pdf(nomor, metadata):
    """Membuat label sumber untuk chunk PDF."""
    halaman = metadata.get("page", "tidak diketahui")
    jenis = metadata.get("jenis", "tidak diketahui")
    nama_file = metadata.get("nama_file") or ""

    if nama_file:
        return (
            f"[Sumber {nomor} | dokumen {nama_file} | "
            f"halaman {halaman} | {jenis}]"
        )

    return f"[Sumber {nomor} | halaman {halaman} | {jenis}]"


def _nama_layanan(metadata):
    """Menentukan nama tampilan untuk chunk web."""
    judul = (metadata.get("judul") or "").strip()
    if judul:
        return judul
    return (metadata.get("nama_file") or "").strip()


def _pasangan_template(metadata):
    """Mengambil pasangan butir -> tautan template dari metadata."""
    nilai = metadata.get("pasangan")
    if not nilai:
        return []

    if isinstance(nilai, str):
        try:
            nilai = json.loads(nilai)
        except (ValueError, TypeError):
            return []

    if not isinstance(nilai, list):
        return []

    hasil = []
    for item in nilai:
        if not isinstance(item, dict):
            continue

        nomor = item.get("no_butir")
        url = item.get("url")
        if not url:
            continue

        hasil.append({"no_butir": nomor, "url": url})

    return hasil


def _baris_tautan_template(metadata):
    """Membuat satu baris tautan template untuk konteks LLM."""
    pasangan = _pasangan_template(metadata)
    if not pasangan:
        return ""

    daftar = "; ".join(
        f"butir {item['no_butir']} -> {item['url']}"
        for item in pasangan
    )
    return f"Tautan template: {daftar}"


def susun_konteks(hasil):
    """
    Menggabungkan chunk hasil retrieval menjadi konteks yang siap
    disisipkan ke prompt LLM.
    """
    daftar_bagian = []

    for nomor, chunk in enumerate(hasil, start=1):
        metadata = chunk.get("metadata") or {}
        jenis = metadata.get("jenis", "tidak diketahui")
        teks = chunk.get("teks", "")

        if jenis == "web":
            nama_layanan = _nama_layanan(metadata)
            if not nama_layanan:
                nama_layanan = "tidak diketahui"

            label = (
                f"[Sumber {nomor} | "
                f"layanan: {nama_layanan} | web]"
            )
        else:
            label = _label_pdf(nomor, metadata)

        bagian = f"{label}\n{teks}"
        tautan = _baris_tautan_template(metadata)
        if tautan:
            bagian += f"\n{tautan}"

        daftar_bagian.append(bagian)

    return "\n\n".join(daftar_bagian)


def format_sumber(hasil, nama_pdf=None):
    """
    Mengubah chunk yang dikirim ke LLM menjadi daftar rujukan sumber resmi.
    """
    halaman_per_dokumen = {}
    daftar_web = []

    for chunk in hasil:
        metadata = chunk.get("metadata") or {}

        if metadata.get("jenis") == "web":
            nama_layanan = _nama_layanan(metadata)
            if nama_layanan and nama_layanan not in daftar_web:
                daftar_web.append(nama_layanan)
            continue

        nomor_halaman = metadata.get("page")
        if nomor_halaman is None:
            continue

        kunci = nama_pdf or metadata.get("nama_file") or ""
        halaman_per_dokumen.setdefault(kunci, set()).add(
            int(nomor_halaman)
        )

    bagian = []

    for nama_file, daftar_halaman in sorted(halaman_per_dokumen.items()):
        halaman_urut = sorted(daftar_halaman)
        daftar_teks = ", ".join(str(nomor) for nomor in halaman_urut)

        if nama_file:
            bagian.append(f"{nama_file}({daftar_teks})")
        else:
            bagian.append(f"halaman {daftar_teks}")

    bagian.extend(daftar_web)
    return "; ".join(bagian)
