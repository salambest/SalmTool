# SalmTool Ultimate

Şəxsi istifadə üçün Android sistem analiz və diaqnostika toolbox-u.
Python + KivyMD ilə yazılıb, Buildozer vasitəsilə birbaşa `.apk` faylına
çevrilir.

> ⚠️ Bu tətbiq **öz cihazını** analiz etmək üçün nəzərdə tutulub (device
> diagnostics, öz APK-larını statik yoxlamaq, öz şəbəkəni analiz etmək və
> s.). APK Security Scanner MobSF kimi açıq mənbəli statik analiz
> alətlərinin sadə versiyasıdır — nəticələr məlumatlandırıcıdır, "kəsin
> hökm" deyil.

## Layihə strukturu

```
SalmTool/
├── main.py                     # Tətbiqin giriş nöqtəsi (MDApp + ScreenManager)
├── buildozer.spec              # Android APK build konfiqurasiyası
├── requirements.txt             # Lokal/dev üçün pip asılılıqları
├── config.json                  # AI Helper API açarı və tənzimləmələr
├── icon.png                      # App icon
├── README.md
│
├── modules/                     # Bütün analiz məntiqi (UI-dan asılı deyil)
│   ├── device_monitor.py
│   ├── apk_analyzer.py
│   ├── apk_security.py
│   ├── network_analyzer.py
│   ├── wifi_analyzer.py
│   ├── exif_analyzer.py
│   ├── hash_checker.py
│   ├── log_analyzer.py
│   ├── file_manager.py
│   ├── root_manager.py
│   ├── ai_helper.py
│   └── report_generator.py
│
└── screens/                     # Hər modul üçün KivyMD UI ekranı
    ├── dashboard.py
    ├── device_monitor_screen.py
    ├── apk_analyzer_screen.py
    ├── apk_security_screen.py
    ├── network_analyzer_screen.py
    ├── wifi_analyzer_screen.py
    ├── exif_analyzer_screen.py
    ├── hash_checker_screen.py
    ├── log_analyzer_screen.py
    ├── file_manager_screen.py
    ├── root_manager_screen.py
    ├── ai_helper_screen.py
    └── reports_screen.py
```

`modules/` mənteqi `screens/`-dəki UI-dan tamamilə ayrıdır — yeni bir
funksiya əlavə etmək üçün sadəcə `modules/` içinə yeni fayl, `screens/`
içinə uyğun ekran yazıb, `main.py`-da `ScreenManager`-ə əlavə etmək
kifayətdir.

## AI Helper API açarı

`config.json` faylını aç və öz Anthropic API açarını yaz:

```json
{
  "ai_helper": {
    "provider": "anthropic",
    "api_key": "sk-ant-...",
    "model": "claude-sonnet-4-6"
  }
}
```

API açarı **heç bir `.py` faylında** saxlanılmır, yalnız runtime-da
`config.json`-dan oxunur (`modules/ai_helper.py`).

## Lokal test (masaüstü)

```bash
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

Kök (root) tələb edən funksiyalar (SELinux, logcat, CPU governor və s.)
masaüstündə avtomatik "mövcud deyil" kimi göstərilir — tətbiq bunsuz da
tam işləyir.

## Android APK yaratmaq (Buildozer)

Linux və ya WSL üzərində:

```bash
pip install buildozer cython
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf \
    libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev

cd SalmTool
buildozer android debug
```

İlk build Android SDK/NDK-nı avtomatik yükləyəcək (uzun çəkə bilər).
Bitdikdə APK burada olacaq:

```
bin/salmtoolultimate-1.0.0-armeabi-v7a_arm64-v8a-debug.apk
```

Faylı telefonuna köçürüb quraşdır (naməlum mənbələrə icazə lazımdır).

## İstifadə axını

1. İstifadəçi `SalmTool.apk`-nı açır.
2. Dashboard-da 12 kart görünür (Device Monitor, APK Analyzer, APK
   Security, Network, WiFi, EXIF, Hash Checker, Log Analyzer, File
   Manager, Root Manager, AI Helper, Reports).
3. Kartlardan birinə toxunur, analiz işə düşür.
4. "SAVE REPORT" düyməsi ilə TXT + JSON + PDF formatında hesabat yaranır
   (`SalmTool/reports/` — cihazda tətbiqin `user_data_dir`-i altında).
5. "Reports" kartından bütün əvvəlki hesabatlar siyahılanır.

## Qeydlər

- **Root tələb olunmur.** `modules/root_manager.py` root olub-olmadığını
  yoxlayır; yoxdursa root-only sahələr sadəcə gizlədilir, tətbiq çökmür.
- **APK Analyzer / Security Scanner** `pyaxmlparser` quraşdırılıbsa ondan,
  yoxdursa daxili heuristik AndroidManifest.xml parserindən istifadə edir
  (bax `modules/apk_analyzer.py`).
- **Scoped storage:** Android 11+ üzərində fayl seçimi `plyer.filechooser`
  vasitəsilə SAF (Storage Access Framework) ilə işləyir; `File Manager`
  modulundakı sərbəst qovluq axtarışı bəzi qovluqlarda əlçatan olmaya
  bilər — bu, Android-in özünün təhlükəsizlik məhdudiyyətidir.
- PDF hesabatları `fpdf2` ilə yaranır; paket quraşdırılmayıbsa
  `save_pdf_report` sadəcə `None` qaytarır, TXT/JSON hesabatları isə hər
  zaman yaranır.
