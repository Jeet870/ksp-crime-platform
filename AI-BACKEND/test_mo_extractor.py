# test_mo_extractor.py
# Tests MO extraction on 5 sample FIR texts
import time
from mo_extractor import extract_mo, mo_to_string

SAMPLE_FIRS = [
    "At approximately 02:30 hours unknown persons cut the electrical supply line at the rear of the premises. They gained entry through the rear window by breaking the iron grille. Gold ornaments weighing 45 grams and cash of Rs 18000 were stolen.",

    "The victim was walking near Koramangala 5th Block signal when two persons on a motorcycle without number plate approached from behind. The pillion rider snatched the gold chain weighing 22 grams from the victim neck and the motorcycle sped away towards Outer Ring Road.",

    "The complainant received a call from an unknown number claiming to be from the State Bank fraud prevention team. The caller convinced the victim to share their OTP for account security. Rs 85000 was subsequently transferred without consent.",

    "The complainant parked their Honda Activa bearing registration KA-05-HB-2341 near Indiranagar 100 Feet Road and upon returning after 2 hours found the vehicle missing. The vehicle was locked at the time.",

    "A group of 4 persons armed with wooden sticks attacked the complainant outside MG Road bus stop at approximately 23:00 hours following a verbal altercation. The victim sustained grievous injuries to the head.",
]

for i, fir_text in enumerate(SAMPLE_FIRS, 1):
    print(f"\n--- FIR {i} ---")
    print(f"Text: {fir_text}...")
    mo = extract_mo(fir_text)
    print(f"MO extracted: {mo}")
    print(f"MO string:    {mo_to_string(mo)}")
    time.sleep(2)  # avoid rate limiting

print("\nAll 5 tests complete")