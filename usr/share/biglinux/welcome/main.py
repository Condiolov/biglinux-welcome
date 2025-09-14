#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
import os
import yaml
import locale
import gettext
from gi.repository import Gtk, Adw, Gio, Gdk
from welcome_page import WelcomePage
from browser_page import BrowserPage
import action_widget

# Set up gettext for application localization.
DOMAIN = 'biglinux-welcome'
LOCALE_DIR = '/usr/share/locale'
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)
gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

# Define a base path for the application's resources
APP_PATH = os.path.dirname(os.path.abspath(__file__))
action_widget.APP_PATH = APP_PATH

class WelcomeWindow(Adw.ApplicationWindow):
    # def __init__(self):
    #     super().__init__(application_id='org.xivastudio.pipewire-proaudio-config')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(800, 600)
        self.set_title("Introduction to BigLinux")

        # Load page data from JSON
        self.pages_data = self.load_pages_data()
        if not self.pages_data:
            self.show_error_page()
            return

        self.build_ui()
        self.update_ui_for_page(0)

    def load_pages_data(self):
        """Loads page definitions from pages.yaml."""
        yaml_path = os.path.join(APP_PATH, "pages.yaml")
        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error loading {yaml_path}: {e}")
            return None

    def build_ui(self):
        """Constructs the main UI."""
        self.header_bar = Adw.HeaderBar()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        main_box.append(self.header_bar)

        # -- Carousel for pages --
        self.carousel = Adw.Carousel()
        self.carousel.connect("page-changed", self.on_page_changed)
        main_box.append(self.carousel)

        # -- Navigation buttons --
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        nav_box.add_css_class("background")
        nav_box.set_halign(Gtk.Align.FILL)
        main_box.append(nav_box)

        self.back_button = Gtk.Button(icon_name="go-previous-symbolic")
        self.back_button.connect("clicked", lambda w: self.carousel.scroll_to(self.carousel.get_nth_page(self.carousel.get_position() - 1), True))
        nav_box.append(self.back_button)

        # Placeholder to push the next button to the end
        spacer = Gtk.Box(hexpand=True)
        nav_box.append(spacer)

        self.next_button = Gtk.Button(icon_name="go-next-symbolic")
        self.next_button.connect("clicked", lambda w: self.carousel.scroll_to(self.carousel.get_nth_page(self.carousel.get_position() + 1), True))
        nav_box.append(self.next_button)

        # -- Progress indicator in HeaderBar --
        self.progress_box = Gtk.Box(spacing=6)
        self.header_bar.set_title_widget(self.progress_box)

        # # Populate carousel and progress bar
        # for i, page_data in enumerate(self.pages_data):
        #     page = WelcomePage(page_data)
        #     self.carousel.append(page)
        #
        #     icon_name = page_data.get("icon", "emblem-default-symbolic")
        #     icon_widget = Gtk.Image.new_from_icon_name(icon_name)
        #     icon_widget.set_pixel_size(24) # Set the desired size
        #
        #     progress_icon = Gtk.Button()
        #     progress_icon.set_child(icon_widget)
        #
        #     progress_icon.set_has_frame(False)
        #     progress_icon.add_css_class("circular")
        #     progress_icon.connect("clicked", self.on_progress_icon_clicked, i)
        #     self.progress_box.append(progress_icon)
        # Populate carousel and progress bar
        for i, page_data in enumerate(self.pages_data):
            # Decide which page type to create
            if page_data.get("page_type") == "browsers":
                page_widget = BrowserPage(page_data, APP_PATH)
            else:
                page_widget = WelcomePage(page_data)

            self.carousel.append(page_widget)

            icon_name = page_data.get("icon", "emblem-default-symbolic")
            icon_widget = Gtk.Image.new_from_icon_name(icon_name)
            icon_widget.set_pixel_size(24) # Set the desired size

            progress_icon = Gtk.Button()
            progress_icon.set_child(icon_widget)

            progress_icon.set_has_frame(False)
            progress_icon.add_css_class("circular")
            progress_icon.connect("clicked", self.on_progress_icon_clicked, i)
            self.progress_box.append(progress_icon)

    def on_page_changed(self, carousel, page_index):
        """Callback for when the carousel page changes."""
        self.update_ui_for_page(page_index)

    def on_progress_icon_clicked(self, button, page_index):
        """Scrolls to the page associated with the clicked progress icon."""
        page_widget = self.carousel.get_nth_page(page_index)
        self.carousel.scroll_to(page_widget, True)

    def update_ui_for_page(self, page_index):
        """Updates HeaderBar title and navigation button sensitivity."""

        # Update progress indicator styles
        child = self.progress_box.get_first_child()
        i = 0
        while child:
            if i < page_index:
                child.add_css_class("suggested-action") # Mark as "done"
                child.remove_css_class("flat")
            elif i == page_index:
                child.add_css_class("flat") # Mark as "current"
                child.remove_css_class("suggested-action")
            else:
                child.remove_css_class("suggested-action") # Mark as "todo"
                child.remove_css_class("flat")

            child = child.get_next_sibling()
            i += 1

        # Update navigation buttons
        self.back_button.set_sensitive(page_index > 0)
        self.next_button.set_sensitive(page_index < self.carousel.get_n_pages() - 1)

    def show_error_page(self):
        """Displays an error if page data cannot be loaded."""
        status_page = Adw.StatusPage(
            icon_name="dialog-error-symbolic",
            title=_("Could Not Load Welcome Pages"),
            description=_("Check if 'pages.yaml' exists and is correctly formatted.")
        )
        self.set_content(status_page)


class BigLinuxWelcome(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='org.biglinux.welcome', **kwargs)
        # ADD: Set color scheme management as recommended by libadwaita
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

        self.connect('activate', self.on_activate)
        self.load_css()

    def load_css(self):
        """Loads custom CSS for the application."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(
            b"""
            .is-not-installed image {
                filter: grayscale(1);
                opacity: 0.7;
            }
            """
        )
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_activate(self, app):
        self.win = WelcomeWindow(application=app)
        self.win.present()

if __name__ == "__main__":
    app = BigLinuxWelcome()
    app.run()
