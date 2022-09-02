import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import aptdaemon
from aptdaemon import client, enums, errors
from aptdaemon.gtk3widgets import AptProgressDialog
import glob


class AptHelper:

    def __init__(self, transient_for=None, modal=False):

        self._cancelled = False
        self.set_packages()

        # Set a function to be run on failure, completion, or cancelled
        # We might want to handle each differently (i.e. enable something on success,
        # ignore if its cancelled, and provide an error message if things go wrong)
        self.success_callback = None
        self.failed_callback = None
        self.cancelled_callback = None

        # Setting modal and a transient_for window somewhat mitigates issues caused
        # when you don't want the app to be used until apt-daemon completes
        self.window = transient_for
        self.modal = modal


    def set_packages(self, install=[], remove=[], purge=[]):
        self.install_list = install
        self.purge_list = remove
        self.remove_list = purge


    def _on_error(self, error):
        # Most likely scenarios for this to run will be because password prompt
        # is cancelled. (NotAuthorizedError), if a bad package name is givien
        # to install (our fault), or if there is no network connection.
        # _on_finished still is run regardless of what we do here, with enums.EXIT_FAILED.

        if type(error) is aptdaemon.errors.NotAuthorizedError:
            # Probably cancelled the password box
            self._cancelled = True


    def _on_failure(self, error):
        error_dialog = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                      buttons=Gtk.ButtonsType.CLOSE,
                                      message_format=error._message)
        error_dialog.run()
        error_dialog.hide()


    def _on_finished(self, dialog):
        self.set_packages()
        if self._cancelled:
            if self.cancelled_callback:
                self.cancelled_callback()
        elif dialog._transaction.exit == enums.EXIT_SUCCESS:
            # What to do when apt is done succesfully
            if self.success_callback:
                self.success_callback()
        elif dialog._transaction.exit == enums.EXIT_FAILED:
            # What to do when apt is fails
            if self.failed_callback:
                self.failed_callback()


    def _on_transaction(self, trans):
        trans.set_remove_obsoleted_depends(remove_obsoleted_depends=True)
        apt_dialog = AptProgressDialog(trans)
        if self.modal and self.window:
            apt_dialog.set_modal(True)
            apt_dialog.set_transient_for(self.window)
        apt_dialog.run(error_handler=self._on_error, show_error=False)
        apt_dialog.connect("finished", self._on_finished)


    def install(self, packages, success_callback=None, failed_callback=None, cancelled_callback=None):
        # Just a simple way to install packages when the rest is unneeded
        self.set_packages(install=packages, remove=[], purge=[])
        self.run(success_callback, failed_callback, cancelled_callback)


    def run(self, success_callback=None, failed_callback=None, cancelled_callback=None):
        # On completion, success_callback function will be run if successful
        # or failed_callback if there was an issue.
        self.success_callback  = success_callback
        self.failed_callback = failed_callback
        self.cancelled_callback = cancelled_callback

        self._cancelled = False

        install =  self.install_list
        remove = []
        purge = []

        # check if requested remove/purge packages are installed
        for pkg in (self.remove_list):
            if pkg != glob.glob('/var/lib/dpkg/info/%s.list' % pkg):
                remove.append(pkg)
        for pkg in (self.purge_list):
            if pkg != glob.glob('/var/lib/dpkg/info/%s.list' % pkg):
                purge.append(pkg)

        if len(install+purge+remove) == 0:
            # Nothing to do
            if self.success_callback:
                self.success_callback()
            return

        apt_client = client.AptClient()
        apt_client.update_cache()
        apt_client.commit_packages(install=install, reinstall=[], remove=remove,
                                   purge=purge, upgrade=[], downgrade=[],
                                   error_handler=self._on_failure,
                                   reply_handler=self._on_transaction)
