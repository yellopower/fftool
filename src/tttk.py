#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import Toplevel, TclError, Label
import tkinter as tk


class Tooltip:
    def __init__(self, widget, text, delay=750, duration=1500):
        self.widget = widget
        self._tooltip = None

        self._hide_id = None
        self._render_id = None
        self._tooltip_text = text
        self._tooltip_delay = delay
        self._tooltip_duration = duration

        self._enter_bind = self.widget.bind("<Enter>", self.show)
        self._leave_bind = self.widget.bind("<Leave>", self.hide)
        self._button_bind = self.widget.bind("<Button>", self.hide)

    def __del__(self):
        try:
            self.widget.unbind("<Enter>", self._enter_bind)
            self.widget.unbind("<Leave>", self._leave_bind)
            self.widget.unbind("<Button>", self._button_bind)
        except TclError:
            pass

    def show(self, _):
        def render():
            if not self._tooltip:
                self._tooltip = tw = Toplevel(self.widget)
                tw.wm_overrideredirect(True)

                x, y = 20, self.widget.winfo_height() + 1
                root_x = self.widget.winfo_rootx() + x
                root_y = self.widget.winfo_rooty() + y
                self._tooltip.wm_geometry("+%d+%d" % (root_x, root_y))

                label = Label(
                    self._tooltip,
                    text=self._tooltip_text,
                    justify='left',
                    background="#ffffe0",
                    relief='solid',
                    borderwidth=1
                )
                label.pack()
                self._tooltip.update_idletasks()  # Needed on MacOS -- see #34275.
                self._tooltip.lift()
                self._hide_id = self.widget.after(self._tooltip_duration, self.hide)

        if self._tooltip_delay:
            if self._render_id:
                self.widget.after_cancel(self._render_id)
            self._render_id = self.widget.after(self._tooltip_delay, render)
        else:
            render()

    def hide(self, _=None):
        try:
            if self._hide_id:
                self.widget.after_cancel(self._hide_id)
            if self._render_id:
                self.widget.after_cancel(self._render_id)
        except TclError:
            pass

        tooltip = self._tooltip
        if self._tooltip:
            try:
                tooltip.destroy()
            except TclError:
                pass
            self._tooltip = None


class StringVar:
    """tk.StringVar 的数据同步对象
    防止在多次给 StringVar 赋值是，windows 路径多次转义的情况。
    例如 "D:\\视频" 会变成 "D:\\\\视频"
    """

    def __init__(self, **kw):
        self.v = tk.StringVar()
        self.datas = []

    def get_object(self):
        """获得 stringvar 对象
        """
        return self.v

    def set(self, arr):
        """设置数据
        会对应改变 stringvar
        """
        tup = tuple(arr)
        self.datas = arr.copy()
        self.v.set(tup)

    def get(self):
        """返回数组
        """
        return self.datas.copy()

    def is_null(self):
        """是否有数据
        """
        # vlstr = self.v.get()
        # vlarr = util.stringVartoList_smb_url(vlstr)
        # util.stringVarisN(vlstr):
        if len(self.datas):
            return False
        else:
            return True


if __name__ == "__main__":
    pass
