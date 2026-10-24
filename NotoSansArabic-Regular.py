# -*- coding: utf-8 -*-
"""Reusable Arabic font/display helper converted to a Kivy library.

Original FontTest functionality is preserved.
"""
import re
import os
from pathlib import Path
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeViewLabel
from kivy.utils import platform
from kivy.factory import Factory  # أضفنا هذه المكتبة لضمان التوافق مع الأندرويد


# ============================
# 1. Arabic shaping detection
# ============================
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SHAPING_READY = True
except Exception:
    arabic_reshaper = None
    get_display = None
    ARABIC_SHAPING_READY = False

# ============================
# 2. Path Isolation (كودك الذكي والمظبوط)
# ============================
if platform == 'android':
    BASE_FONT_DIR = Path(os.path.dirname(__file__))
else:
    BASE_FONT_DIR = Path("/storage/emulated/0/Download/mainemp")

ARABIC_FONT_PATH = BASE_FONT_DIR / "NotoSansArabic-Regular.ttf"
ARABIC_FONT_NAME = "NotoArabic"
ARABIC_FONT_READY = False

# ============================
# 3. Font Registration
# ============================
try:
    if ARABIC_FONT_PATH.exists():
        LabelBase.register(
            name=ARABIC_FONT_NAME,
            fn_regular=str(ARABIC_FONT_PATH)
        )
        ARABIC_FONT_READY = True
        print("Arabic font registered successfully inside APK!")
    else:
        print(f"Font file not found at: {ARABIC_FONT_PATH}")
except Exception as e:
    ARABIC_FONT_READY = False
    print(f"Font registration failed: {repr(e)}")

# ========================================================
# 4. Arabic Text Processing Function (محرك إصلاح الكلمات)
# ========================================================
def reshape_text(text):
    if not text or not isinstance(text, str):
        return text
    # التحقق إذا كان النص يحتوي على حوف عربية
    if ARABIC_SHAPING_READY and re.search(r'[\u0600-\u06FF]', text):
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text

# ========================================================
# 5. Kivy Core Widgets Override (إجبار الأندرويد على تشغيل الخط)
# ========================================================
if ARABIC_FONT_READY:
    # تعديل سلوك النصوص داخل الـ Label
    original_label_init = Label.__init__
    def new_label_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', ARABIC_FONT_NAME)
        if 'text' in kwargs:
            kwargs['text'] = reshape_text(kwargs['text'])
        original_label_init(self, *args, **kwargs)
    Label.__init__ = new_label_init

    # تعديل سلوك النصوص داخل الـ Button
    original_button_init = Button.__init__
    def new_button_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', ARABIC_FONT_NAME)
        if 'text' in kwargs:
            kwargs['text'] = reshape_text(kwargs['text'])
        original_button_init(self, *args, **kwargs)
    Button.__init__ = new_button_init

    # تعديل سلوك النصوص داخل الـ TextInput
    original_textinput_init = TextInput.__init__
    def new_textinput_init(self, *args, **kwargs):
        kwargs.setdefault('font_name', ARABIC_FONT_NAME)
        original_textinput_init(self, *args, **kwargs)
    TextInput.__init__ = new_textinput_init

    
# ================
# CENTRAL FONT / ARABIC DISPLAY CLASS
# ================
class FontTest:
    """
    CENTRAL FONT / ARABIC DISPLAY CLASS.
    Anything displayed to the user passes through this class.
    Raw data remains separate from its screen representation.
    """
    # -------------
    # Regular expressions
    # -------------
    _ARABIC_RE = re.compile(
        r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]"
    )

    _LATIN_RE = re.compile(
        r"[A-Za-z]")
    _DIGIT_RE = re.compile(
        r"[0-9\u0660-\u0669]")
    _URL_RE = re.compile(
        r"^(?:https?://|www\.)",
        re.IGNORECASE)
    # ------------
    # Unicode direction characters
    # -----------
    _DIRECTION_CHARS = (
        "\u202A" "\u202B" "\u202C" "\u202D" "\u202E"
        "\u2066" "\u2067" "\u2068" "\u2069" "\u200E"
        "\u200F")
    # =================
    # fix
    # ==============
    @classmethod
    def fix(cls, text):
        if text is None:
            return ""
        return str(text).translate(str.maketrans(
                "","",cls._DIRECTION_CHARS))
    # ==============
    # direction
    # ===========
    @classmethod
    def direction(cls, text):
        value = cls.fix(text).lstrip()
        if not value:
            return "ltr"
        for ch in value:
            if cls._ARABIC_RE.match(ch):
                return "rtl"
            if (
                cls._LATIN_RE.match(ch)
                or cls._DIGIT_RE.match(ch)):
                return "ltr"
        return "ltr"
    # ==================
    # process
    # =================
    @classmethod
    def process(cls, text):
        raw = cls.fix(text)
        direction = cls.direction(raw)
        if not raw:
            return raw, raw, direction

        if (
            direction == "ltr"
            and not cls._ARABIC_RE.search(raw)):
            return raw, raw, direction
        if ARABIC_SHAPING_READY:
            try:
                shaped = arabic_reshaper.reshape(raw)
                visual = get_display(shaped)
                return raw, visual, direction
            except Exception:
                return raw, raw, direction
        return raw, raw, direction

    # ============
    # display
    # ==============

    @classmethod
    def display(cls, text):

        _raw, visual, _direction = cls.process(text)

        return visual

    # ========================================================
    # input_process
    # ========================================================

    @classmethod
    def input_process(
        cls,
        current_text,
        inserted_text,
        cursor_index=None,
        selection_start=None,
        selection_end=None,
    ):

        current = cls.fix(current_text)

        inserted = cls.fix(inserted_text)

        if cursor_index is None:
            cursor_index = len(current)

        if (
            selection_start is not None
            and selection_end is not None
            and selection_start != selection_end
        ):

            a, b = sorted(
                (
                    int(selection_start),
                    int(selection_end)
                )
            )

            current = (
                current[:a]
                + current[b:]
            )

            cursor_index = a

        cursor_index = max(
            0,
            min(
                int(cursor_index),
                len(current)
            )
        )

        return cls.fix(
            current[:cursor_index]
            + inserted
            + current[cursor_index:]
        )

    # ========================================================
    # apply
    # ========================================================

    @classmethod
    def apply(cls, widget, text=None):

        if text is None:

            text = getattr(
                widget,
                "_fonttest_raw_text",
                getattr(widget, "text", "")
            )

        raw, visual, direction = cls.process(text)

        widget._fonttest_raw_text = raw

        if hasattr(widget, "text"):
            widget.text = visual

        if (
            ARABIC_FONT_READY
            and hasattr(widget, "font_name")
        ):
            widget.font_name = ARABIC_FONT_NAME

        if hasattr(widget, "halign"):

            widget.halign = (
                "right"
                if direction == "rtl"
                else "left"
            )

        return raw, visual, direction

    # ==============
    # label

    @classmethod
    def label(cls, text="", **kwargs):

        widget = Label(
            text="",
            **kwargs
        )

        cls.apply(
            widget,
            text
        )

        return widget

    # ========================================================
    # button
    # ========================================================

    @classmethod
    def button(cls, text="", **kwargs):

        widget = Button(
            text="",
            **kwargs
        )

        cls.apply(
            widget,
            text
        )

        return widget


# ============================================================
# Arabic Label
# ============================================================
class ArabicLabel(Label):

    def __init__(self, **kwargs):

        # ----------------------------------------------------
        # أخذ النص الأصلي
        # ----------------------------------------------------

        raw_text = kwargs.pop(
            "text",
            ""
        )

        # ----------------------------------------------------
        # إعدادات الخط
        # ----------------------------------------------------

        kwargs.setdefault(
            "font_name",
            ARABIC_FONT_NAME
        )

        kwargs.setdefault(
            "halign",
            "right"
        )

        kwargs.setdefault(
            "valign",
            "middle"
        )

        # ----------------------------------------------------
        # إنشاء Label بدون نص
        # ----------------------------------------------------

        super().__init__(
            text="",
            **kwargs
        )

        # ----------------------------------------------------
        # المتغيرات الداخلية
        # ----------------------------------------------------

        self._fonttest_raw_text = ""

        self._fonttest_setting_text = False

        # ----------------------------------------------------
        # مراقبة أي تغيير في النص
        # ----------------------------------------------------

        self.bind(
            text=self._fonttest_text_changed
        )

        # ----------------------------------------------------
        # حجم النص
        # ----------------------------------------------------

        self.text_size = self.size

        self.bind(
            size=self._sync_text_size
        )

        # ----------------------------------------------------
        # النص الأولي
        # ----------------------------------------------------

        self.set_text(
            raw_text
        )

    # ========================================================
    # مراقبة تغيير text
    # ========================================================

    def _fonttest_text_changed(
        self,
        instance,
        value
    ):

        # ----------------------------------------------------
        # لو التغيير صادر من داخل الكلاس نفسه
        # لا نعيد المعالجة
        # ----------------------------------------------------

        if self._fonttest_setting_text:
            return

        # ----------------------------------------------------
        # أي نص خارجي يمر من FontTest
        # ----------------------------------------------------

        raw, visual, direction = FontTest.process(
            value
        )

        # ----------------------------------------------------
        # حفظ النص الأصلي
        # ----------------------------------------------------

        self._fonttest_raw_text = raw

        # ----------------------------------------------------
        # وضع النص المرئي
        # ----------------------------------------------------

        self._fonttest_setting_text = True

        try:

            self.text = visual

        finally:

            self._fonttest_setting_text = False

        # ----------------------------------------------------
        # الخط
        # ----------------------------------------------------

        if ARABIC_FONT_READY:

            self.font_name = ARABIC_FONT_NAME

        # ----------------------------------------------------
        # الاتجاه
        # ----------------------------------------------------

        self.halign = (
            "right"
            if direction == "rtl"
            else "left"
        )

    # ========================================================
    # Text size
    # ========================================================

    def _sync_text_size(
        self,
        *_
    ):

        self.text_size = self.size

    # ========================================================
    # Change text
    # ========================================================

    def set_text(
        self,
        text
    ):

        raw, visual, direction = FontTest.process(
            text
        )

        self._fonttest_raw_text = raw

        self._fonttest_setting_text = True

        try:

            self.text = visual

        finally:

            self._fonttest_setting_text = False

        if ARABIC_FONT_READY:

            self.font_name = ARABIC_FONT_NAME

        self.halign = (
            "right"
            if direction == "rtl"
            else "left"
        )

        return (
            raw,
            visual,
            direction
        )

    # ========================================================
    # Raw text
    # ========================================================

    @property
    def raw_text(self):

        return FontTest.fix(
            self._fonttest_raw_text
        )

    def get_raw_text(self):

        return FontTest.fix(
            self._fonttest_raw_text
        )

# ============================================================
# Arabic Button
# ============================================================

class ArabicButton(Button):

    def __init__(self, **kwargs):

        raw_text = kwargs.pop(
            "text",
            ""
        )

        kwargs.setdefault(
            "font_name",
            ARABIC_FONT_NAME
        )

        kwargs.setdefault(
            "halign",
            "center"
        )

        kwargs.setdefault(
            "valign",
            "middle"
        )

        super().__init__(
            text="",
            **kwargs
        )

        self._fonttest_raw_text = ""

        self._fonttest_setting_text = False

        self.text_size = self.size

        self.bind(
            size=self._sync_text_size
        )

        # ----------------------------------------------------
        # أي نص عند إنشاء Button
        # يمر إجباريًا من FontTest
        # ----------------------------------------------------

        self.set_text(
            raw_text
        )

    # ========================================================
    # Text size
    # ========================================================

    def _sync_text_size(
        self,
        *_
    ):

        self.text_size = self.size

    # ========================================================
    # Change text
    # ========================================================

    def set_text(
        self,
        text
    ):

        raw, visual, direction = FontTest.process(
            text
        )

        self._fonttest_raw_text = raw

        self._fonttest_setting_text = True

        try:

            self.text = visual

        finally:

            self._fonttest_setting_text = False

        if ARABIC_FONT_READY:

            self.font_name = ARABIC_FONT_NAME

        # ----------------------------------------------------
        # الزر يظل مركزيًا
        # ----------------------------------------------------

        self.halign = "center"

        self.valign = "middle"

        return (
            raw,
            visual,
            direction
        )

    # ========================================================
    # Raw text
    # ========================================================

    def get_raw_text(self):

        return self._fonttest_raw_text

    @property
    def raw_text(self):

        return self._fonttest_raw_text


# ============================================================
# Arabic TextInput
# ============================================================
 # ============================================================
# Arabic TextInput
# ============================================================

class ArabicTextInput(TextInput):

    def __init__(self, **kwargs):

        # ----------------------------------------------------
        # إعدادات أساسية
        # ----------------------------------------------------

        kwargs.setdefault(
            "multiline",
            False
        )

        kwargs.setdefault(
            "halign",
            "right"
        )

        kwargs.setdefault(
            "font_name",
            ARABIC_FONT_NAME
        )

        # ----------------------------------------------------
        # أخذ النص الأصلي
        # ----------------------------------------------------

        raw_text = kwargs.pop(
            "text",
            ""
        )

        # ----------------------------------------------------
        # إنشاء TextInput
        # ----------------------------------------------------

        super().__init__(
            text="",
            **kwargs
        )

        # ----------------------------------------------------
        # الحالة الداخلية
        # ----------------------------------------------------

        self._fonttest_raw_text = ""

        self._fonttest_setting_text = False

        self._fonttest_editing = False

        # ----------------------------------------------------
        # مراقبة النص
        # ----------------------------------------------------

        self.bind(
            text=self._fonttest_text_changed
        )

        # ----------------------------------------------------
        # مراقبة التركيز
        # ----------------------------------------------------

        self.bind(
            focus=self._fonttest_focus_changed
        )

        # ----------------------------------------------------
        # النص الأولي
        # ----------------------------------------------------

        self.set_raw_text(
            raw_text
        )

    # ========================================================
    # text changed
    # ========================================================

    def _fonttest_text_changed(
        self,
        instance,
        value
    ):

        # ----------------------------------------------------
        # تغيير داخلي
        # ----------------------------------------------------

        if self._fonttest_setting_text:

            return

        # ----------------------------------------------------
        # أثناء الكتابة
        # ----------------------------------------------------

        if self._fonttest_editing:

            self._fonttest_raw_text = FontTest.fix(
                value
            )

            return

        # ----------------------------------------------------
        # تغيير خارجي
        # ----------------------------------------------------

        self._fonttest_raw_text = FontTest.fix(
            value
        )

    # ========================================================
    # focus changed
    # ========================================================

    def _fonttest_focus_changed(
        self,
        instance,
        focused
    ):

        # ----------------------------------------------------
        # دخل وضع الكتابة
        # ----------------------------------------------------

        if focused:

            self._fonttest_editing = True

            # ------------------------------------------------
            # النص المرئي
            # ------------------------------------------------

            raw, visual, direction = FontTest.process(
                self._fonttest_raw_text
            )

            self._fonttest_setting_text = True

            try:

                self.text = visual

            finally:

                self._fonttest_setting_text = False

            # ------------------------------------------------
            # الاتجاه
            # ------------------------------------------------

            if direction == "rtl":

                self.halign = "right"

            else:

                self.halign = "left"

            # ------------------------------------------------
            # المؤشر في النهاية
            # ------------------------------------------------

            try:

                self.cursor = (
                    len(self.text),
                    0
                )

            except Exception:

                pass

            return

        # ----------------------------------------------------
        # خرج من وضع الكتابة
        # ----------------------------------------------------

        self._fonttest_editing = False

        # ----------------------------------------------------
        # الاحتفاظ بالنص الحالي
        # ----------------------------------------------------

        self._fonttest_raw_text = FontTest.fix(
            self._fonttest_raw_text
        )

        # ----------------------------------------------------
        # إعادة معالجة النص
        # ----------------------------------------------------

        raw, visual, direction = FontTest.process(
            self._fonttest_raw_text
        )

        if direction == "rtl":

            self.halign = "right"

        else:

            self.halign = "left"

        self._fonttest_setting_text = True

        try:

            self.text = visual

        finally:

            self._fonttest_setting_text = False

    # ========================================================
    # insert_text
    # ========================================================
    def insert_text(
        self,
        substring,
        from_undo=False
    ):
        # ----------------------------------------------------
        # النص الذي سيتم إدخاله
        # ----------------------------------------------------
        inserted = FontTest.fix(
            substring
        )
        if not inserted:
            return
        # ----------------------------------------------------
        # النص الحالي الحقيقي
        # ----------------------------------------------------
        raw = self._fonttest_raw_text
        # ----------------------------------------------------
        # موضع المؤشر
        # ----------------------------------------------------
        try:
            cursor_index = self.cursor_index()
        except Exception:
            cursor_index = len(raw)
        # ----------------------------------------------------
        # تحديد التحديد
        # ----------
        selection_start = None
        selection_end = None
        if self.selection_text:
            try:
                selection_start = self.selection_from()
                selection_end = self.selection_to()
            except Exception:
                selection_start = None
                selection_end = None
        # ----------------------------------------------------
        # بناء النص الحقيقي الجديد
        # ----------------------------------------------------
        new_raw = FontTest.input_process(
            raw,
            inserted,
            cursor_index,
            selection_start,
            selection_end)
        self._fonttest_raw_text = new_raw
        # -----------------
        # معالجة النص للعرض
        _raw, visual, direction = FontTest.process(
            new_raw )
        # -----------
        # تحديث العرض
        self._fonttest_setting_text = True
        try: self.text = visual
        finally:
            self._fonttest_setting_text = False
        # -----------
        # الاتجاه
        if direction == "rtl":self.halign = "right"
        else: self.halign = "left"
        # -------------
        # إلغاء التحديد
        try: self.cancel_selection()
        except Exception:
            pass
    # =====================
    # do_backspace
    def do_backspace(
        self,from_undo=False,mode="bkspc"):
        raw = self._fonttest_raw_text
        if not raw:
            return
        # -----------
        # موضع المؤشر
        try:
            cursor_index = self.cursor_index()
        except Exception:
            cursor_index = len(raw)
        # ---------------------
        # حذف التحديد أولًا
        if self.selection_text:
            try:
                selection_start = self.selection_from()
                selection_end = self.selection_to()
                a, b = sorted((
                        selection_start,
                        selection_end ))
                new_raw = (  raw[:a] + raw[b:])
            except Exception:
                new_raw = raw
        else:
            # -----------
            # Backspace
            if cursor_index <= 0:
                return
            new_raw = ( raw[:cursor_index - 1]
                + raw[cursor_index:])
        # ------------
        # حفظ النص الحقيقي
        self._fonttest_raw_text = new_raw
        # --------------
        # معالجة العرض
        _raw, visual, direction = FontTest.process(
            new_raw)
        self._fonttest_setting_text = True
        try:
            self.text = visual
        finally:
            self._fonttest_setting_text = False
        # -----------------
        # الاتجاه
        if direction == "rtl":
            self.halign = "right"
        else:
            self.halign = "left"
        # -------------
        # إلغاء التحديد
        try:
            self.cancel_selection()
        except Exception:
            pass
    # ===================
    # raw_text property
    @property
    def raw_text(self):
        return FontTest.fix(self._fonttest_raw_text )
    # ===================
    # get_raw_text
    def get_raw_text(self):
        return FontTest.fix(self._fonttest_raw_text)
    # ===========
    # set_raw_text
    def set_raw_text(self, text):
        # ---------------
        # تنظيف النص
        raw = FontTest.fix(  text  )
        self._fonttest_raw_text = raw
        # ------------
        # اتجاه النص
        direction = FontTest.direction( raw  )
        if direction == "rtl":
            self.halign = "right"
        else:
            self.halign = "left"
        # -----------------
        # تجهيز النص المرئي
        _raw, visual, _direction = FontTest.process(
            raw )
        # ------------------
        # عرض النص
        self._fonttest_setting_text = True
        try:
            self.text = visual
        finally:
            self._fonttest_setting_text = False
        # ------------
        # الخط
        if ARABIC_FONT_READY:
            self.font_name = ARABIC_FONT_NAME
        return ( raw, visual, direction )
    # ===================
    # set_display_text
    def set_display_text( self,text):
        return self.set_raw_text( text )
    # ====================
    # input_process
    def input_process(
        self,
        inserted_text,
        cursor_index=None,
        selection_start=None,
        selection_end=None):
        return FontTest.input_process(
            self.get_raw_text(),
            inserted_text,
            cursor_index,
            selection_start,
            selection_end)
    # =====================
    # set_text
    def set_text( self,text):
        return self.set_raw_text( text)
# =====================نهاية الكلاس=======================================

# ============================================================
# Arabic TreeView Label
# ============================================================

class ArabicTreeLabel(TreeViewLabel):

    def __init__(self, **kwargs):
        raw_text = kwargs.pop("text", "")

        kwargs.setdefault("font_name", ARABIC_FONT_NAME)
        kwargs.setdefault("halign", "right")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", 42)

        super().__init__(text="", **kwargs)

        self._fonttest_raw_text = ""
        self.record_index = -1

        self.bind(width=self._sync_text_size)
        self._sync_text_size()

        self.set_text(raw_text)

    def _sync_text_size(self, *_):
        self.text_size = self.size

    def set_text(self, text):
        raw, visual, direction = FontTest.process(text)

        self._fonttest_raw_text = raw

        if ARABIC_FONT_READY:
            self.font_name = ARABIC_FONT_NAME

        self.halign = "right" if direction == "rtl" else "left"

        if self.text != visual:
            self.text = visual

        return raw, visual, direction

    @property
    def raw_text(self):
        return FontTest.fix(self._fonttest_raw_text)

    def get_raw_text(self):
        return FontTest.fix(self._fonttest_raw_text)
        
# Simple compatibility function
def fonttest(text):
    return FontTest.fix(text)
# ===============
# Information
def font_info():
    return {
        "name": ARABIC_FONT_NAME,
        "path": str(ARABIC_FONT_PATH),
        "exists": ARABIC_FONT_PATH.exists(),
        "ready": ARABIC_FONT_READY,
        "arabic_shaping_ready": ARABIC_SHAPING_READY,
    }
# =====================
# Test

Factory.register("ArabicLabel", cls=ArabicLabel)
Factory.register("ArabicButton", cls=ArabicButton)
Factory.register("ArabicTextInput", cls=ArabicTextInput)
if __name__ == "__main__":
    print(
        "=============================")