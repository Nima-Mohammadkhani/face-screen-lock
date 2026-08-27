import tkinter as tk
from tkinter import ttk

from config_utils import load_config, save_config
from i18n import get_language, set_language, t

AWAY_OPTIONS = [2, 5, 10, 15, 30, 60, 120]
INTERVAL_OPTIONS = [1, 2, 3, 5]
COOLDOWN_OPTIONS = [15, 30, 60, 120]
ACTIVITY_GRACE_OPTIONS = [2, 5, 10, 15]
ACTIVITY_OVERRIDE_MAX_OPTIONS = [30, 60, 120, 300]
UNRECOGNIZED_FACE_OPTIONS = [2, 3, 5, 10, 15]
ADAPT_INTERVAL_OPTIONS = [5, 10, 20, 30]
ADAPT_MAX_SAMPLES_OPTIONS = [40, 80, 120, 200]
MEETING_MULTIPLIER_OPTIONS = [2, 3, 5, 10]

LANGUAGE_LABELS = ["English", "فارسی"]
LANGUAGE_VALUES = ["en", "fa"]


def _is_rtl():
    return get_language() == "fa"


def _sensitivity_options():
    return [
        (t("opt_sensitivity_strict"), 50),
        (t("opt_sensitivity_medium"), 70),
        (t("opt_sensitivity_relaxed"), 90),
    ]


def _adapt_confidence_options():
    return [
        (t("opt_adapt_very_cautious"), 20),
        (t("opt_adapt_cautious"), 40),
        (t("opt_adapt_relaxed"), 60),
    ]


class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        set_language(self.config_data.get("language", "en"))
        self.resizable(False, False)
        self._build_ui()
        self.eval("tk::PlaceWindow . center")

    def _save(self, key, value):
        self.config_data[key] = value
        save_config(self.config_data)

    def _change_language(self, language):
        self._save("language", language)
        set_language(language)
        selected = self.notebook.index(self.notebook.select()) if hasattr(self, "notebook") else 0
        self._build_ui(selected_tab_index=selected)

    def _build_ui(self, selected_tab_index=0):
        for child in self.winfo_children():
            child.destroy()

        self.title(t("settings_title"))
        rtl = _is_rtl()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self._build_basic_tab(self.notebook)
        self._build_activity_tab(self.notebook)
        self._build_adaptive_tab(self.notebook)
        self._build_meeting_tab(self.notebook)

        try:
            self.notebook.select(selected_tab_index)
        except tk.TclError:
            pass

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(bottom, text=t("settings_close"), command=self.destroy).pack(
            side="left" if rtl else "right"
        )

    def _prepare_tab(self, tab):
        if _is_rtl():
            tab.grid_columnconfigure(0, weight=1)

    def _combo_row(self, parent, row, label_text, key, options, value_formatter=None):
        rtl = _is_rtl()
        label_col, value_col = (2, 1) if rtl else (0, 1)
        label_padx = (10, 0) if rtl else (0, 10)
        value_sticky = "e" if rtl else "w"

        ttk.Label(parent, text=label_text).grid(
            row=row, column=label_col, sticky="e", padx=label_padx, pady=6
        )

        if options and isinstance(options[0], tuple):
            labels = [o[0] for o in options]
            values = [o[1] for o in options]
        else:
            values = options
            labels = [value_formatter(v) if value_formatter else str(v) for v in values]

        var = tk.StringVar()
        combo = ttk.Combobox(
            parent,
            textvariable=var,
            values=labels,
            state="readonly",
            width=36,
            justify="right" if rtl else "left",
        )
        current = self.config_data.get(key)
        if current in values:
            combo.current(values.index(current))
        combo.grid(row=row, column=value_col, sticky=value_sticky, pady=6)

        def on_select(event=None, values=values, labels=labels, key=key):
            idx = labels.index(var.get())
            self._save(key, values[idx])

        combo.bind("<<ComboboxSelected>>", on_select)
        return combo

    def _check_row(self, parent, row, label_text, key, default=True, on_toggle=None):
        rtl = _is_rtl()
        var = tk.BooleanVar(value=self.config_data.get(key, default))

        def on_change():
            self._save(key, var.get())
            if on_toggle:
                on_toggle(var.get())

        chk = ttk.Checkbutton(parent, text=label_text, variable=var, command=on_change)
        chk.grid(
            row=row,
            column=1 if rtl else 0,
            columnspan=2,
            sticky="e" if rtl else "w",
            pady=(0, 12),
        )
        return var

    @staticmethod
    def _set_children_state(widgets, enabled):
        for w in widgets:
            if isinstance(w, ttk.Combobox):
                w.configure(state="readonly" if enabled else "disabled")
            else:
                w.configure(state="normal" if enabled else "disabled")

    def _build_basic_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=18)
        notebook.add(tab, text=t("tab_basic"))
        self._prepare_tab(tab)
        rtl = _is_rtl()
        label_col, value_col = (2, 1) if rtl else (0, 1)
        label_padx = (10, 0) if rtl else (0, 10)
        value_sticky = "e" if rtl else "w"

        ttk.Label(tab, text=t("field_language")).grid(
            row=0, column=label_col, sticky="e", padx=label_padx, pady=6
        )
        lang_var = tk.StringVar()
        lang_combo = ttk.Combobox(
            tab,
            textvariable=lang_var,
            values=LANGUAGE_LABELS,
            state="readonly",
            width=36,
            justify="right" if rtl else "left",
        )
        current_lang = self.config_data.get("language", "en")
        if current_lang in LANGUAGE_VALUES:
            lang_combo.current(LANGUAGE_VALUES.index(current_lang))
        lang_combo.grid(row=0, column=value_col, sticky=value_sticky, pady=6)

        def on_lang_select(event=None):
            idx = LANGUAGE_LABELS.index(lang_var.get())
            self._change_language(LANGUAGE_VALUES[idx])

        lang_combo.bind("<<ComboboxSelected>>", on_lang_select)

        ttk.Separator(tab, orient="horizontal").grid(
            row=1, column=1 if rtl else 0, columnspan=2, sticky="ew", pady=(4, 10)
        )

        self._combo_row(
            tab, 2, t("field_away_threshold"), "away_seconds_threshold",
            AWAY_OPTIONS, lambda v: t("opt_seconds", v=v),
        )
        self._combo_row(
            tab, 3, t("field_check_interval"), "check_interval_seconds",
            INTERVAL_OPTIONS, lambda v: t("opt_every_seconds", v=v),
        )
        self._combo_row(
            tab, 4, t("field_sensitivity"), "confidence_threshold", _sensitivity_options()
        )
        self._combo_row(
            tab, 5, t("field_lock_cooldown"), "lock_cooldown_seconds",
            COOLDOWN_OPTIONS, lambda v: t("opt_seconds", v=v),
        )

    def _build_activity_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=18)
        notebook.add(tab, text=t("tab_activity"))
        self._prepare_tab(tab)
        rtl = _is_rtl()

        sub_widgets = []

        def toggle(enabled):
            self._set_children_state(sub_widgets, enabled)

        self._check_row(tab, 0, t("field_enabled"), "require_activity_check", True, toggle)

        sub_widgets.append(
            self._combo_row(
                tab, 1, t("field_activity_grace"), "activity_grace_seconds",
                ACTIVITY_GRACE_OPTIONS, lambda v: t("opt_seconds", v=v),
            )
        )
        sub_widgets.append(
            self._combo_row(
                tab, 2, t("field_activity_override_max"), "activity_override_max_seconds",
                ACTIVITY_OVERRIDE_MAX_OPTIONS, lambda v: t("opt_seconds", v=v),
            )
        )

        stranger_var = tk.BooleanVar(
            value=self.config_data.get("lock_faster_on_unrecognized_face", True)
        )

        def on_stranger_change():
            self._save("lock_faster_on_unrecognized_face", stranger_var.get())

        stranger_chk = ttk.Checkbutton(
            tab,
            text=t("field_lock_faster_on_stranger"),
            variable=stranger_var,
            command=on_stranger_change,
        )
        stranger_chk.grid(
            row=3,
            column=1 if rtl else 0,
            columnspan=2,
            sticky="e" if rtl else "w",
            pady=(6, 12),
        )
        sub_widgets.append(stranger_chk)

        sub_widgets.append(
            self._combo_row(
                tab, 4, t("field_unrecognized_face_threshold"),
                "unrecognized_face_seconds_threshold",
                UNRECOGNIZED_FACE_OPTIONS, lambda v: t("opt_seconds", v=v),
            )
        )

        toggle(self.config_data.get("require_activity_check", True))

    def _build_adaptive_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=18)
        notebook.add(tab, text=t("tab_adaptive"))
        self._prepare_tab(tab)

        sub_widgets = []

        def toggle(enabled):
            self._set_children_state(sub_widgets, enabled)

        self._check_row(tab, 0, t("field_enabled"), "adaptive_learning", True, toggle)

        sub_widgets.append(
            self._combo_row(
                tab, 1, t("field_adapt_interval"), "adaptive_learning_interval_minutes",
                ADAPT_INTERVAL_OPTIONS, lambda v: t("opt_every_minutes", v=v),
            )
        )
        sub_widgets.append(
            self._combo_row(
                tab, 2, t("field_adapt_confidence"),
                "adaptive_learning_confidence_threshold", _adapt_confidence_options(),
            )
        )
        sub_widgets.append(
            self._combo_row(
                tab, 3, t("field_adapt_max_samples"), "adaptive_learning_max_samples",
                ADAPT_MAX_SAMPLES_OPTIONS, lambda v: t("opt_samples", v=v),
            )
        )

        toggle(self.config_data.get("adaptive_learning", True))

    def _build_meeting_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=18)
        notebook.add(tab, text=t("tab_meeting"))
        self._prepare_tab(tab)

        sub_widgets = []

        def toggle(enabled):
            self._set_children_state(sub_widgets, enabled)

        self._check_row(tab, 0, t("field_enabled"), "meeting_mode_enabled", True, toggle)
        sub_widgets.append(
            self._combo_row(
                tab, 1, t("field_meeting_multiplier"), "meeting_mode_multiplier",
                MEETING_MULTIPLIER_OPTIONS, lambda v: t("opt_multiplier", v=v),
            )
        )

        toggle(self.config_data.get("meeting_mode_enabled", True))


def main():
    app = SettingsWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
