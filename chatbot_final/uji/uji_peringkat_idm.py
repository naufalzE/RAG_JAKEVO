# ============================================================
# uji_peringkat_idm.py
# Menguji peringkat chunk IDM tanpa memanggil LLM.
# Jalankan (dari folder chatbotv2): python uji/uji_peringkat_idm.py
# ============================================================

from _bootstrap import cocok_id

from database import buka_collection
from embedding import muat_model
from retriever import retriever


PERTANYAAN = "Kenapa SK izin saya tidak muncul di layar?"
ID_TARGET = "TXT-P034-C001"
TOPK_UJI = 20


def main():
    collection = buka_collection()
    model = muat_model()

    hasil = retriever(
        collection=collection,
        model=model,
        pertanyaan=PERTANYAAN,
        topk=TOPK_UJI,
    )

    print("\n" + "=" * 60)
    print("HASIL UJI PERINGKAT CHUNK IDM")
    print("=" * 60)
    print(f"Pertanyaan: {PERTANYAAN}")
    print(f"Jumlah hasil: {len(hasil)}")
    print(f"ID target: {ID_TARGET}")

    peringkat_target = None

    for peringkat, chunk in enumerate(hasil, start=1):
        metadata = chunk["metadata"]

        # cocok_id() mengakomodasi awalan kode dokumen pada chunk_id.
        cocok = cocok_id(chunk["chunk_id"], ID_TARGET)

        if cocok:
            peringkat_target = peringkat

        penanda = " <<< TARGET IDM" if cocok else ""

        print(f"\nPeringkat : {peringkat}{penanda}")
        print(f"Chunk ID  : {chunk['chunk_id']}")
        print(f"Halaman   : {metadata.get('page')}")
        print(f"Distance  : {chunk['distance']}")
        print(f"Teks      : {chunk['teks'][:250]}")

    print("\n" + "-" * 60)

    if peringkat_target is not None:
        print(
            f"TARGET DITEMUKAN pada peringkat "
            f"{peringkat_target}."
        )
    else:
        print(
            f"TARGET TIDAK MASUK dalam {TOPK_UJI} hasil teratas."
        )

    print("=" * 60)


if __name__ == "__main__":
    main()