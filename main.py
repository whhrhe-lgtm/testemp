# -*- coding: utf-8 -*-
import json, os, tempfile, importlib.util, re
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, date

from kivy.app import App
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView
from kivy.uix.popup import Popup
from jnius import autoclass, PythonJavaClass, java_method
import sys
import traceback
from kivy.utils import platform

try:
    import arabic_reshaper
except Exception as e:
    arabic_reshaper = None
    print("arabic_reshaper unavailable:", repr(e))

try:
    from bidi.algorithm import get_display
except Exception as e:
    get_display = None
    print("python-bidi unavailable:", repr(e))

# ==========================================
# 1. ضبط مسار المجلد الأساسي المشترك بأمان
# ==========================================
if platform == 'android':
    # يقرأ من مجلد المطور الداخلي المعزول والآمن للـ APK على الهاتف
    BASE_DIR = Path(os.path.dirname(__file__))
else:
    # يقرأ من مجلد التحميلات أثناء تجربة الكود على الكمبيوتر الشخصي
    BASE_DIR = Path("/storage/emulated/0/Download/mainemp")

# ==========================================
# 2. ربط واستدعاء ملف قاعدة البيانات
# ==========================================
DATA_FILE = BASE_DIR / "phone.json"

# ==========================================
# 3. الحل: استدعاء وتشغيل مكتبة الخطوط العربية تلقائياً
# ==========================================
try:
    # هذا السطر السحري يجبر البرنامج على تشغيل ملف خطوطك المخصص فوراً وحقنه داخل كائنات Kivy
    import NotoSansArabic_Regular  # لاحظ أن بايثون تستبدل الشرطة الناقصة (-) بشرطة سفلية (_) أو تأكد من مطابقة اسم ملفك النصي
    print("Arabic Font Script imported successfully!")
except Exception as font_error:
    print("Could not import Arabic Font Script:", repr(font_error))



FONT_FILE = BASE_DIR / "NotoSansArabic-Regular.py"

WHATSAPP_NUMBER = "201205332285"  # عدّل الرقم إلى رقم واتساب الكامل


WHATSAPP_NUMBERS = [
    ("وليد", "201032575310"),
    ("ايهاب ", "201205332285"),
    (" رامى", "201271135901"),
    (" جوزيف", "201208508546"),
    (" جمال", "201288887654"),
]

FIELDS = [
    "name", "shop", "health_card", "expiry_date", "id_card",
    "job", "current_status", "data_review", "attendance", "phone"
]

FIELD_NAMES = {
    "name": "الاسم",
    "shop": "مكان العمل",
    "health_card": "رقم السيارة",
    "expiry_date": "انتهاء الشهادة",
    "id_card": "البطاقة",
    "job": "المهنة",
    "current_status": "مسموح الدخول ",
    "data_review": "مطلوب لمكتب الامن",
    "attendance": "وقت الحضور",
    "phone": "رقم التليفون"
}

BG = (.055, .075, .12, 1)
CARD = (.10, .13, .19, 1)
WHITE = (.94, .96, .99, 1)
FORM_BG = (0.94, 0.96, 0.98, 1)
FORM_CARD = (1, 1, 1, 1)
FORM_TITLE = (0.10, 0.22, 0.38, 1)
FORM_TEXT = (0.20, 0.25, 0.32, 1)
FORM_ACCENT = (0.12, 0.38, 0.68, 1)

try:
    spec = importlib.util.spec_from_file_location("NotoArabicLibrary", FONT_FILE)
    if spec is None or spec.loader is None:
        raise ImportError("Arabic helper not found")

    arabic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arabic)

    ArabicLabel = arabic.ArabicLabel
    ArabicButton = arabic.ArabicButton
    ArabicTextInput = arabic.ArabicTextInput
    ArabicTreeLabel = arabic.ArabicTreeLabel

except Exception as e:
    print("Arabic helper fallback:", e)

    from kivy.core.text import LabelBase
    from kivy.uix.label import Label as KLabel
    from kivy.uix.button import Button as KButton
    from kivy.uix.textinput import TextInput as KInput
    from kivy.uix.treeview import TreeViewLabel as KTreeLabel

    FONT_NAME = "Roboto"

    font_paths = [
        Path("/system/fonts/NotoNaskhArabicUI-Regular.ttf"),
        Path("/system/fonts/NotoNaskhArabic-Regular.ttf"),
        Path("/system/fonts/NotoSansArabic-Regular.ttf"),
        BASE_DIR / "NotoSansArabic-Regular.ttf",
    ]

    for font_path in font_paths:
        if font_path.is_file():
            try:
                LabelBase.register(
                    name="AndroidArabic",
                    fn_regular=str(font_path)
                )
                FONT_NAME = "AndroidArabic"
                print("Arabic font found:", font_path)
                break
            except Exception as err:
                print("Font load failed:", err)

    def shape_ar(text):
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)

    class ArabicLabel(KLabel):
        def __init__(self, text="", **kw):
            self._raw_text = str(text)
            super().__init__(
                text=shape_ar(text),
                font_name=FONT_NAME,
                **kw
            )

        def set_text(self, text):
            self._raw_text = str(text)
            self.text = shape_ar(text)

    class ArabicButton(KButton):
        def __init__(self, text="", **kw):
            super().__init__(
                text=shape_ar(text),
                font_name=FONT_NAME,
                **kw
            )

    class ArabicTreeLabel(KTreeLabel):
        def __init__(self, text="", **kw):
            super().__init__(
                text=shape_ar(text),
                font_name=FONT_NAME,
                **kw
            )

    class ArabicTextInput(KInput):
        def __init__(self, **kw):
            kw.setdefault("font_name", FONT_NAME)
            super().__init__(**kw)

        def get_raw_text(self):
            return self.text

        def set_raw_text(self, text):
            self.text = str(text)


def al(text="", **kw):
    return ArabicLabel(text=str(text), **kw)


#def ab(text="", **kw):
   # return ArabicButton(text=str(text), **kw)
def ab(text="", **kw):
    kw.setdefault("font_size", sp(10))
    kw.setdefault("size_hint_y", None)
    kw.setdefault("height", dp(55))
    return ArabicButton(text=str(text), **kw)

def ai(**kw):
    return ArabicTextInput(**kw)


def raw_text(w):
    try:
        return w.get_raw_text()
    except Exception:
        return w.text


def set_raw(w, text):
    try:
        w.set_raw_text(str(text))
    except Exception:
        w.text = str(text)

def normalize(text):
    text = str(text or "").strip().lower()
    for a, b in [
        ("أ", "ا"), ("إ", "ا"), ("آ", "ا"),
        ("ى", "ي"), ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")
    ]:
        text = text.replace(a, b)
    return re.sub(r"[\u064b-\u065f\u0670ـ]", "", text)


def load_json():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_json(data):
    fd, path = tempfile.mkstemp(dir=BASE_DIR, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(path, DATA_FILE)
    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass
        raise
        



ERROR_FILE = Path(__file__).resolve().parent / "error.log"


def log_error(error):
    try:
        with open(ERROR_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 40}\n")
            f.write(f"{datetime.now()}\n")

            if isinstance(error, BaseException):
                f.write("".join(traceback.format_exception(
                    type(error), error, error.__traceback__
                )))
            else:
                f.write(str(error))

            f.write("\n")
            f.flush()
    except Exception:
        pass


def handle_error(exc_type, exc_value, exc_traceback):
    log_error(exc_value)


sys.excepthook = handle_error


class MyErrorHandler(ExceptionHandler):
    def handle_exception(self, inst):
        log_error(inst)
        return ExceptionManager.PASS


ExceptionManager.add_handler(MyErrorHandler())
  
        
class UIRunnable(PythonJavaClass):
    __javainterfaces__ = ["java/lang/Runnable"]

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method("()V")
    def run(self):
        self.callback()


class NativeTextWatcher(PythonJavaClass):
    __javainterfaces__ = ["android/text/TextWatcher"]

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method("(Ljava/lang/CharSequence;III)V")
    def beforeTextChanged(self, s, start, count, after):
        pass

    @java_method("(Ljava/lang/CharSequence;III)V")
    def onTextChanged(self, s, start, before, count):
        self.callback(str(s) if s is not None else "")

    @java_method("(Landroid/text/Editable;)V")
    def afterTextChanged(self, s):
        pass


class EditorActionListener(PythonJavaClass):
    __javainterfaces__ = ["android/widget/TextView$OnEditorActionListener"]

    def __init__(self, app):
        super().__init__()
        self.app = app

    @java_method("(Landroid/widget/TextView;ILandroid/view/KeyEvent;)Z")
    def onEditorAction(self, view, action_id, event):
        Clock.schedule_once(lambda dt: self.app.search(), 0)
        return True


class Card(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(*CARD)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(16)]
            )
        self.bind(pos=self.draw_bg, size=self.draw_bg)

    def draw_bg(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class EmployeeApp(App):
    

    def build(self):
        Window.clearcolor = BG
        self.records = load_json()
        self.selected = None
        self.native_edit = None
        self.native_watcher = None
        self.native_listener = None
        self.native_syncing = False
        self.message_popup = None
    
        root = BoxLayout(
            orientation="vertical",
            padding=dp(10), spacing=dp(9)
        )
    
        # Main header
        header = Card(
            orientation="vertical",
            padding=dp(8),
            size_hint_y=None, height=dp(52)
        )
        header.add_widget(al(
            "إدارة بيانات المحلات",
            font_size=sp(17), color=WHITE,
            halign="center", valign="middle"
        ))
        root.add_widget(header)
    
        # Search section
        search_card = Card(
            orientation="horizontal",
            padding=dp(8), spacing=dp(8),
            size_hint_y=None, height=dp(56)
        )
        self.search_input = ai(
            hint_text="اكتب اسم الموظف أو المحل...",
            multiline=False, size_hint_x=1
        )
        self.search_input.bind(
            on_text_validate=lambda *x: self.search()
        )
        search_card.add_widget(self.search_input)
        search_card.add_widget(ab(
            text="بحث",
            size_hint_x=None, width=dp(72),
            on_release=lambda *x: self.search()
        ))
        root.add_widget(search_card)
    
        # Employees list section
        list_card = Card(
            orientation="vertical",
            padding=dp(8), spacing=dp(5),
            size_hint_y=.38
        )
        list_card.add_widget(al(
            "قائمة الموظفين",
            font_size=sp(14), color=WHITE,
            size_hint_y=None, height=dp(28),
            halign="right", valign="middle"
        ))
    
        self.tree = TreeView(
            hide_root=True, indent_level=1,
            size_hint_y=None
        )
        self.tree.bind(
            minimum_height=self.tree.setter("height")
        )
        self.tree_scroll = ScrollView(
            do_scroll_x=False
        )
        self.tree_scroll.add_widget(self.tree)
        list_card.add_widget(self.tree_scroll)
        root.add_widget(list_card)
    
        # Employee details section
        #Employee details and vertical action buttons
    
        main_area = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=1
        )
    
        # Employee details card
        self.details_card = Card(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(4),
            size_hint_x=.76
        )
    
        self.details_card.add_widget(al(
            "بيانات الموظف",
            font_size=sp(14),
            color=WHITE,
            size_hint_y=None,
            height=dp(28),
            halign="right",
            valign="middle"
        ))
    
        self.details_scroll = ScrollView(
            do_scroll_x=False
        )
    
        self.details_label = al(
            "ابحث عن موظف لعرض بياناته",
            size_hint_y=None,
            halign="right",
            valign="top",
            color=WHITE
        )
    
        self.details_label.bind(
            width=lambda w, width: setattr(
                w, "text_size", (width, None)
            ),
            texture_size=lambda w, size: setattr(
                w, "height", size[1]
            )
        )
    
        self.details_scroll.add_widget(self.details_label)
        self.details_card.add_widget(self.details_scroll)
  
        main_area.add_widget(self.details_card)
    
        # Vertical action buttons
        buttons = BoxLayout(
            orientation="vertical",
            spacing=dp(1),
            padding=(0, dp(8)),
            pos_hint={"top": 1.1},
            size_hint_x=.15
        )
        buttons.add_widget(ab(
text="حضور",
on_release=lambda *x: self.register_attendance()
))
    
        buttons.add_widget(ab(
            text="إضافة",
            on_release=lambda *x: self.open_form()
        ))
    
        buttons.add_widget(ab(
            text="تعديل",
            on_release=lambda *x: (
                self.open_form(self.selected)
                if self.selected is not None
                else self.message("تنبيه", "اختر موظفًا أولًا")
            )
        ))
    
        buttons.add_widget(ab(
            text="حذف",
            on_release=lambda *x: self.confirm_delete()
        ))
    
        
    
        buttons.add_widget(ab(
            text="MSG ",
            on_release=lambda *x: self.open_whatsapp_selection()
        ))
        buttons.add_widget(ab(
            text="إغلاق",
            on_release=lambda *x: self.stop()
        ))
       
        main_area.add_widget(buttons)
        root.add_widget(main_area)
                
        
    
        
      
      
          
        self.refresh_tree()
        Clock.schedule_once(
            self.start_native_editor, .5
        )
        return root

    
    
     
    
    
    
    
        
            
    def refresh_tree(self, query="", search_shop=False):
        self.tree.clear_widgets()
        self.tree.root.nodes.clear()
        q = normalize(query)

        for i, rec in enumerate(self.records):
            name = str(rec.get("name", "بدون اسم"))
            shop = str(rec.get("shop", "بدون محل"))

            if q:
                if search_shop:
                    if q not in normalize(shop):
                        continue
                elif q not in normalize(name):
                    continue

            node = ArabicTreeLabel(
                text=f"{name} - {shop}",
                font_size=sp(12), size_hint_y=None,
                height=dp(42), color=WHITE
            )
            node.record_index = i
            node.bind(
                on_touch_down=lambda w, t, n=node:
                self.on_node_selected(n)
                if w.collide_point(*t.pos) else None
            )
            self.tree.add_node(node)
            

    def search(self, *args):
        query = raw_text(self.search_input).strip()
        normalized_query = normalize(query)

        if "محل" in normalized_query:
            shop_query = normalized_query.split("محل", 1)[1].strip()

            if not shop_query:
                self.details_label.set_text("اكتب اسم المحل للبحث")
                self.refresh_tree()
                return

            self.refresh_tree(shop_query, search_shop=True)
            self.selected = None
            count = sum(
                1 for r in self.records
                if shop_query in normalize(r.get("shop", ""))
            )

            if count:
                self.details_label.set_text(
                    f"عدد العمال في المحل: {count}\n"
                    "اختر اسم الموظف من القائمة لعرض بياناته"
                )
            else:
                self.details_label.set_text(
                    "لم يتم العثور على عمال في هذا المحل"
                )
            return

        self.refresh_tree(query)
        q = normalize(query)
        matches = [
            (i, r) for i, r in enumerate(self.records)
            if q and q in normalize(r.get("name", ""))
        ]

        if len(matches) == 1:
            self.selected = matches[0][0]
            self.show_details(self.records[self.selected])
        elif not query:
            self.details_label.set_text("اكتب اسم الموظف للبحث")
        elif not matches:
            self.details_label.set_text(
                "لم يتم العثور على موظف بهذا الاسم"
            )
            self.selected = None
        else:
            self.details_label.set_text(
                "تم العثور على أكثر من موظف، اختر الاسم من القائمة"
            )
            self.selected = None

    def on_node_selected(self, node, *args):
        self.selected = node.record_index
        self.show_details(self.records[self.selected])
        
        
        

    
    def show_details(self, record):
        try:
            lines = []
            expiry = str(record.get("expiry_date", "")).strip()
            expired = False
    
            if expiry:
                for fmt in ("%d/%m/%Y", "%d/%m/%y","%dd/%mm/%yy"):
                    try:
                        expiry_date = datetime.strptime(
                            expiry, fmt
                        ).date()
                        expired = expiry_date < date.today()
                        
                        break
                    except (ValueError, TypeError):
                        continue
    
            for key, value in record.items():
                if key == "code":
                    continue
    
                label = FIELD_NAMES.get(key, key)
                lines.append(
                    f"{label}: {value if value else 'غير مسجل'}"
                )
    
            text = "\n".join(lines) or "لا توجد بيانات"
    
            self.details_label.set_text(text)
            self.details_label.texture_update()
            self.details_label.height = (
                self.details_label.texture_size[1] + dp(350)
            )
    
            self.details_label.color = (
                (1, 0, 0, 1) if expired else WHITE
            )
    
        except Exception as e:
            log_error("SHOW DETAILS ERROR: " + repr(e))
            self.details_label.set_text("تعذر عرض بيانات الموظف")
            self.details_label.color = WHITE

    def open_whatsapp_selection(self):
        if self.selected is None:
            self.message(
                "تنبيه",
                "اختر موظفًا من القائمة أولًا"
            )
            return

        record = self.records[self.selected]

        lines = [
            f"{FIELD_NAMES.get(key, key)}: {value}"
            for key, value in record.items()
            if key != "code" and str(value or "").strip()
        ]

        if not lines:
            self.message("تنبيه", "لا توجد بيانات لإرسالها")
            return

        from kivy.uix.checkbox import CheckBox

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        layout.add_widget(al(
            "اختر للارسال",
            color=WHITE,
            size_hint_y=None,
            height=dp(40)
        ))

        scroll = ScrollView(do_scroll_x=False)

        items = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None
        )
        items.bind(minimum_height=items.setter("height"))

        checks = []

        for label, number in WHATSAPP_NUMBERS:
            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(45),
                spacing=dp(8)
            )

            check = CheckBox(
                size_hint_x=None,
                width=dp(45)
            )

            row.add_widget(check)
            row.add_widget(al(
                label,
                color=WHITE,
                halign="right",
                valign="middle"
            ))

            items.add_widget(row)
            checks.append((check, number, label))

        scroll.add_widget(items)
        layout.add_widget(scroll)

        row_buttons = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        popup = Popup(
            title="send",
            content=layout,
            size_hint=(.4, .70)
        )

        def send_selected(*args):
            targets = [
                (number.strip(), label)
                for check, number, label in checks
                if check.active
                and number.strip()
                and "X" not in number.upper()
            ]

            if not targets:
                self.message(
                    "تنبيه",
                    "اختر رقم واتساب   "
                )
                return

            popup.dismiss()

            message_text = quote("\n".join(lines))
            state = {"index": 0}

            def open_current(*args):
                i = state["index"]

                if i >= len(targets):
                    self.message(
                        "تم",
                        "انتهت قائمة الأرقام المحددة"
                    )
                    return

                number, label = targets[i]
                number = number.strip().replace("+", "").replace(" ", "")

                if number.startswith("0"):
                    number = "2" + number[1:]

                try:
                    Intent = autoclass("android.content.Intent")
                    Uri = autoclass("android.net.Uri")
                    PythonActivity = autoclass(
                        "org.kivy.android.PythonActivity"
                    )

                    url = (
                        "https://wa.me/"
                        + number
                        + "?text="
                        + message_text
                    )

                    intent = Intent(
                        Intent.ACTION_VIEW,
                        Uri.parse(url)
                    )

                    PythonActivity.mActivity.startActivity(intent)
                    state["index"] += 1

                    if state["index"] < len(targets):
                        Clock.schedule_once(
                            lambda dt: show_next_prompt(),
                            0.5
                        )
            #        else:
                 #       Clock.schedule_once(
                         #   lambda dt: self.message(
                           #     "انتهى",
                    #            "تم فتح آخر محادثة محددة. "
           #                     "اضغط إرسال داخل واتساب لإرسال الرسالة."
                     #       ),
           #                 0.5
                 #       )

                except Exception as e:
                    log_error("WHATSAPP ERROR: " + repr(e))
                    self.message(
                        "خطأ",
                        "تعذر فتح محادثة "
                        + label + "\n" + str(e)
                    )

            def show_next_prompt():
                box = BoxLayout(
                    orientation="vertical",
                    padding=dp(12),
                    spacing=dp(10)
                )

                box.add_widget(al(
                    "ارجع إلى البرنامج بعد الانتهاء من المحادثة الحالية، "
                    "ثم اضغط متابعة لفتح الرقم التالي.",
                    color=WHITE
                ))

                next_popup = Popup(
                    title="متابعة الإرسال",
                    content=box,
                    size_hint=(.9, .4)
                )

                box.add_widget(ab(
                    text="متابعة",
                    size_hint_y=None,
                    height=dp(45),
                    on_release=lambda *x: continue_next()
                ))

                box.add_widget(ab(
                    text="إنهاء",
                    size_hint_y=None,
                    height=dp(45),
                    on_release=lambda *x: next_popup.dismiss()
                ))

                def continue_next():
                    next_popup.dismiss()
                    open_current()

                next_popup.open()

            open_current()

        row_buttons.add_widget(ab(
            text="إرسال",
            on_release=send_selected
        ))

        row_buttons.add_widget(ab(
            text="إلغاء",
            on_release=lambda *x: popup.dismiss()
        ))

        layout.add_widget(row_buttons)
        popup.open()
    
    
    
    
        
        
    def open_form(self, index=None):
            editing = index is not None
            record = self.records[index].copy() if editing else {}
            inputs = {}
        
            layout = BoxLayout(
                orientation="vertical",
                padding=dp(12), spacing=dp(10)
            )
        
            # Header
            header = BoxLayout(
                size_hint_y=None, height=dp(52),
                padding=(dp(12), 0)
            )
            header.add_widget(al(
                "تعديل بيانات الموظف" if editing else "إضافة موظف جديد",
                color=WHITE, font_size=sp(17),
                halign="right", valign="middle"
            ))
        
            # Scrollable form
            scroll = ScrollView(do_scroll_x=False)
            content = BoxLayout(
                orientation="vertical", spacing=dp(12),
                size_hint_y=None, padding=(dp(2), dp(4))
            )
            content.bind(minimum_height=content.setter("height"))
        
            groups = {
                "البيانات الشخصية": {
                    "name", "phone", "id_card", "health_card"
                },
                "بيانات العمل": {
                    "shop", "job", "current_status",
                    "data_review", "attendance"
                },
                "التواريخ والمستندات": {
                    "expiry_date"
                },
                "بيانات إضافية": set()
            }
        
            sections = {title: [] for title in groups}
        
            for key in FIELDS:
                group = next(
                    (title for title, keys in groups.items()
                    if key in keys),
                    "بيانات إضافية"
                )
                sections[group].append(key)
        
            def set_attendance_time(inp, touch):
                if inp.collide_point(*touch.pos) and touch.is_double_tap:
                    set_raw(inp, datetime.now().strftime("%H:%M"))
                return False
                #*******""***********""""""
                
                
          
                
                         #*******""***********""""""
                
        
            for title, keys in sections.items():
                if not keys:
                    continue
        
                card = BoxLayout(
                    orientation="vertical",
                    padding=dp(12), spacing=dp(9),
                    size_hint_y=None
                )
                card.bind(minimum_height=card.setter("height"))
        
                with card.canvas.before:
                    Color(*FORM_CARD)
                    bg = RoundedRectangle(
                        pos=card.pos, size=card.size,
                        radius=[dp(14)]
                    )
        
                card.bind(
                    pos=lambda w, p, r=bg: setattr(r, "pos", p),
                    size=lambda w, s, r=bg: setattr(r, "size", s)
                )
        
                card.add_widget(al(
                    title, size_hint_y=None, height=dp(38),
                    color=FORM_TITLE, font_size=sp(15),
                    halign="right", valign="middle"
                ))
        
                for key in keys:
                    field = BoxLayout(
                        orientation="vertical",
                        spacing=dp(4), size_hint_y=None,
                        height=dp(72)
                    )
        
                    field.add_widget(al(
                        FIELD_NAMES.get(key, key),
                        size_hint_y=None, height=dp(25),
                        color=FORM_TEXT, font_size=sp(12),
                        halign="right", valign="middle"
                    ))
        
                    inp = ai(
                        text=str(record.get(key, "")),
                        multiline=False,
                        size_hint_y=None, height=dp(43),
                        hint_text=FIELD_NAMES.get(key, key),
                        foreground_color=FORM_TEXT,
                        cursor_color=FORM_ACCENT
                    )
        
                    if key == "attendance":
                        inp.bind(on_touch_down=set_attendance_time)
        
                    field.add_widget(inp)
                    card.add_widget(field)
                    inputs[key] = inp
        
                content.add_widget(card)
        
            scroll.add_widget(content)
            layout.add_widget(header)
            layout.add_widget(scroll)
        
            # Fixed bottom buttons
            row = BoxLayout(
                size_hint_y=None, height=dp(50),
                spacing=dp(8)
            )
        
            popup = Popup(
                title="",
                content=layout,
                size_hint=(.95, .90),
                background_color=FORM_BG,
                separator_height=dp(0)
            )
        
            def save(*args):
                try:
                    new_record = {
                        k: raw_text(v).strip()
                        for k, v in inputs.items()
                    }
        
                    if not new_record.get("name"):
                        self.message("تنبيه", "اكتب اسم الموظف")
                        return
        
                    if editing:
                        self.records[index].update(new_record)
                    else:
                        self.records.append(new_record)
        
                    if not self.save_records():
                        return
        
                    popup.dismiss()
                    self.refresh_tree(new_record["name"])
                    self.selected = index if editing else len(self.records) - 1
                    self.show_details(self.records[self.selected])
                    set_raw(self.search_input, new_record["name"])
        
                    Clock.schedule_once(
                        lambda dt: self.message(
                            "نجاح", "تم حفظ البيانات في الملف"
                        ), .3
                    )
        
                except Exception as e:
                    traceback.print_exc()
                    self.message("خطأ", repr(e))
        

        
            row.add_widget(ab(
                text="حفظ", on_release=save
            ))
      #      row.add_wid
            row.add_widget(ab(
                text="إلغاء", on_release=lambda *x: popup.dismiss()
            ))
        
            layout.add_widget(row)
        
            # Keep Android editor visibility workaround unchanged.
            popup.open()
            
            
    
    def register_attendance(self):
        if self.selected is None:
         self.message("تنبيه", "اختر موظفًا أولًا")
         return
        
        self.records[self.selected]["attendance"] = datetime.now().strftime("%I:%M %p")
        
        if self.save_records():
            self.show_details(self.records[self.selected])
            self.message("تم", "تم تسجيل وقت الحضور وحفظه بنجاح")
            
    def save_records(self):
        try:
            save_json(self.records)
            return True
        except Exception as e:
            self.message("خطأ", "تعذر حفظ البيانات:\n" + str(e))
            return False
            
            

    def confirm_delete(self):
     if self.selected is None:
        self.message("تنبيه", "اختر موظفًا أولًا")
        return

     layout = BoxLayout(
        orientation="vertical",
        padding=dp(12),
        spacing=dp(12)
    )

     layout.add_widget(
        al("هل تريد حذف الموظف؟", color=WHITE)
    )

     row = BoxLayout(
        size_hint_y=None,
        height=dp(45),
        spacing=dp(8)
    )

     popup = Popup(
        title="تأكيد الحذف",
        content=layout,
        size_hint=(.8, .3)
    )

     row.add_widget(ab(
        text="حذف",
        on_release=lambda *x: (
            self.delete_record(),
            popup.dismiss()
        )
    ))

     row.add_widget(ab(
        text="إلغاء",
        on_release=lambda *x: popup.dismiss()
    ))

     layout.add_widget(row)
     popup.open()

    def delete_record(self):
        if self.selected is None:
            return
        del self.records[self.selected]
        self.selected = None
        if self.save_records():
            self.refresh_tree()
            self.details_label.set_text("تم حذف الموظف")
            
            

    
        
        
        
    def message(self, title, text):
        if self.message_popup is not None:
          if self.message_popup.parent is not None:
             return
          self.message_popup = None

        box = BoxLayout(
        orientation="vertical", padding=dp(12), spacing=dp(10)
    )
        box.add_widget(al(text, color=WHITE))

        pop = Popup(
        title=title, content=box, size_hint=(.85, .35)
    )
        self.message_popup = pop

        def close_message(*args):
           pop.dismiss()
           if self.message_popup is pop:
            self.message_popup = None

        box.add_widget(ab(
        text="إغلاق",
        size_hint_y=None,
        height=dp(42),
        on_release=close_message
    ))

        pop.bind(on_dismiss=lambda *args: setattr(
        self, "message_popup", None
    ) if self.message_popup is pop else None)

        pop.open()
        
        
        

    def start_native_editor(self, dt=None):
        try:
            activity = autoclass(
                "org.kivy.android.PythonActivity"
            ).mActivity
            activity.runOnUiThread(UIRunnable(self.create_native_editor))
        except Exception as e:
            print("NATIVE START ERROR:", e)

    def create_native_editor(self):
         if self.native_edit is not None:
            return

         try:
            EditText = autoclass("android.widget.EditText")
            Params = autoclass(
                "android.widget.FrameLayout$LayoutParams"
            )
            JavaColor = autoclass("android.graphics.Color")
            JavaString = autoclass("java.lang.String")
            Gravity = autoclass("android.view.Gravity")

            activity = autoclass(
                "org.kivy.android.PythonActivity"
            ).mActivity

            edit = EditText(activity)
            edit.setSingleLine(True)
            edit.setTextSize(16)
            edit.setBackgroundColor(JavaColor.WHITE)
            edit.setHint(JavaString("اكتب أو استخدم ميكروفون"))
            edit.setTextColor(JavaColor.BLACK)

            watcher = NativeTextWatcher(
                self.native_text_changed
            )
            listener = EditorActionListener(self)

            edit.addTextChangedListener(watcher)
            edit.setOnEditorActionListener(listener)

            density = activity.getResources().getDisplayMetrics().density

            params = Params(
                int(240 * density),
                int(40 * density)
            )
            params.leftMargin = int(20 * density)
            params.topMargin = int(80 * density)
            params.gravity = Gravity.TOP | Gravity.LEFT

            activity.addContentView(edit, params)

            self.native_edit = edit
            self.native_watcher = watcher
            self.native_listener = listener

            edit.requestFocus()

         except Exception as e:
            log_error("NATIVE EDIT ERROR: " + repr(e))
            self.native_edit = None
            self.native_watcher = None
            self.native_listener = None

         except Exception as e:
            print("NATIVE EDIT ERROR:", e)

    def native_text_changed(self, text):
        if self.native_syncing:
            return
        Clock.schedule_once(
            lambda dt: self.copy_native_to_kivy(text), 0
        )

    def copy_native_to_kivy(self, text):
        try:
            self.native_syncing = True
            set_raw(self.search_input, text or "")
        finally:
            self.native_syncing = False

    

    
    def sync_native_text(self, text):
        if not self.native_edit:
            return

        try:
            activity = autoclass(
                "org.kivy.android.PythonActivity"
            ).mActivity

            edit = self.native_edit
            JavaString = autoclass("java.lang.String")
            java_text = JavaString(str(text))

            def update_text():
                try:
                    self.native_syncing = True
                    edit.setText(java_text)
                except Exception as e:
                    print("NATIVE SETTEXT ERROR:", e)
                finally:
                    self.native_syncing = False

            activity.runOnUiThread(UIRunnable(update_text))

        except Exception as e:
            print("NATIVE SYNC ERROR:", e)
    
    
    

    def show_native_editor(self, visible):
        if not self.native_edit:
            return
        try:
            activity = autoclass(
                "org.kivy.android.PythonActivity"
            ).mActivity
            edit = self.native_edit

            def change_visibility():
                View = autoclass("android.view.View")
                edit.setVisibility(
                    View.VISIBLE if visible else View.GONE
                )

            activity.runOnUiThread(UIRunnable(change_visibility))

        except Exception as e:
            print("NATIVE VISIBILITY ERROR:", e)


if __name__ == "__main__":
    EmployeeApp().run()