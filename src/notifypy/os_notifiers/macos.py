import os
import pathlib
import subprocess
import sys
import appdirs

from src.utils import logger, resource_path
from ..exceptions import BinaryNotFound, InvalidMacOSNotificator
from ._base import BaseNotifier


class MacOSNotifier(BaseNotifier):
    def __init__(self, **kwargs):
        """Main macOS Notification System, supplied by a custom-made notificator app.
        Icon Support is **not** supported. You'll need to create your own bundle for that.
        """

        if kwargs.get("custom_mac_notificator"):
            """This optional kwarg exists for the use of using a custom (made) notificator without building a .whl"""
            selected_custom_notificator = kwargs.get("custom_mac_notificator")
            if (
                pathlib.Path(selected_custom_notificator)
                / "Contents/Resources/Scripts/notificator"
            ).exists():
                current_selected_binary = pathlib.Path(
                    selected_custom_notificator
                ).absolute()
                if os.access(
                    (
                        current_selected_binary
                        / "Contents/Resources/Scripts/notificator"
                    ),
                    os.X_OK,
                ):
                    self._notificator_binary = str(
                        current_selected_binary
                        / "Contents/Resources/Scripts/notificator"
                    )
                else:
                    raise InvalidMacOSNotificator(
                        "Unable to access binary, you might need to update the permissions."
                    )
            else:
                raise InvalidMacOSNotificator
        else:
            call_find_notificator = self._find_bundled_notificator()
            if not call_find_notificator:
                logger.error("Unable to find Bundled Notificator")
                raise BinaryNotFound("bundled notifcator.")
            if call_find_notificator:
                self._notificator_binary = call_find_notificator

        call_find_afplay = self._find_installed_afplay()
        if not call_find_afplay:
            # no Afplay is available.
            self._afplay_binary = False
        else:
            self._afplay_binary = call_find_afplay

    @staticmethod
    def _find_bundled_notificator():
        """Gets the bundled Notifcator"""
        try:
            if getattr(sys, "frozen", False):
                current_bundled = os.path.join(
                    appdirs.user_data_dir("VSingerBoard"),
                    "Notificator.app",
                    "Contents",
                    "MacOS",
                    "applet",
                )
            else:
                current_bundled = os.path.join(
                    resource_path("Notificator.app"),
                    "Contents",
                    "MacOS",
                    "applet",
                )
            if pathlib.Path(current_bundled).exists():
                return current_bundled
            raise BinaryNotFound("bundled notifier.app")
        except Exception as e:
            logger.exception(f"Unhandled exception for finding afplay.:{e}")
            raise

    @staticmethod
    def _find_installed_afplay():
        """Function to find the path for afplay"""
        try:
            run_which_for_aplay = subprocess.check_output(["which", "afplay"])
            return run_which_for_aplay.decode("utf-8")
        except subprocess.CalledProcessError:
            logger.exception("Unable to find aplay.")
            return False
        except Exception as e:
            logger.exception(f"Unhandled exception for finding aplay.:{e}")
            return False

    def send_notification(
        self,
        notification_title,
        notification_subtitle,
        application_name,
        notification_audio,
        **kwargs
    ):
        if kwargs.get("notification_icon"):
            logger.warning(
                "Notification icon is not supported. Read the docs for more information."
            )

        try:
            logger.info(f"Sending Notification: {notification_title}, {notification_subtitle}, {application_name}")
            notification_title = " " if notification_title == "" else notification_title
            notification_subtitle = (
                " " if notification_subtitle == "" else notification_subtitle
            )

            if notification_audio:

                if self._afplay_binary == False:
                    raise BinaryNotFound("afplay")

                subprocess.Popen(
                    [self._afplay_binary.strip(), notification_audio],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )

            generated_command = [
                self._notificator_binary,
                notification_subtitle,
                application_name,
                notification_title,
            ]

            subprocess.check_output(generated_command)
            return True
        except subprocess.CalledProcessError as e:
            logger.exception(f"Unable to send notification.:{e}")
            return False
        except Exception as e:
            logger.exception(f"Unhandled Exception for sending notifications:{e}")
            return False
