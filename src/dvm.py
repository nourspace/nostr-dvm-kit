from enum import IntEnum
from typing import Any

import structlog
from nostr_sdk import EventBuilder, Tag, Client, EventId, Filter, Timestamp, HandleNotification
from pydantic import BaseModel, ConfigDict


class BaseKinds(IntEnum):
    pass


class DefaultKinds(BaseKinds):
    KIND_1_NOTE = 1
    KIND_7_REACTION = 1
    KIND_31990_DVM_ANNOUNCEMENT = 31990


# Todo (Nour): add display_name, encryption, ...
class AnnouncementDict(BaseModel):
    name: str
    display_name: str = None
    about: str
    image: str
    picture: str = None


class NotificationHandler(HandleNotification):
    def __init__(self, *args, dvm, **kwargs):
        super().__init__(*args, **kwargs)
        self.dvm: BaseDVM = dvm

    def handle(self, relay_url, event):
        self.dvm.handle(relay_url, event)

    def handle_msg(self, relay_url, msg):
        self.dvm.handle_msg(relay_url, msg)


class BaseDVM(BaseModel):
    name: str
    client: Client
    kinds: list[int]
    announcement_id: EventId = None
    announcement_dict: AnnouncementDict = None

    notification_handler_class: Any = NotificationHandler
    log: structlog.BoundLogger = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.log = structlog.get_logger(logger_name=self._name)

    @property
    def _name(self):
        return f"{self.__class__.__name__}({self.name})"

    def build_and_send_announcement(self):
        if self.announcement_id is not None:
            self.log.info(f"Already announced {self.announcement_id}")
            return
        content = self.announcement_dict.model_dump_json()
        tags = [
            # Todo (Nour): find better d tag
            Tag.parse(["d", self.announcement_dict.name]),
            *[Tag.parse(["k", str(kind)]) for kind in self.kinds],
        ]
        builder = EventBuilder(kind=DefaultKinds.KIND_31990_DVM_ANNOUNCEMENT, content=content, tags=tags)
        self.announcement_id = self.client.send_event_builder(builder=builder)
        self.log.info(f"Announced {self.announcement_id.to_bech32()}")

    def listen_to_kinds(self):
        reqs_filter = Filter().kinds(kinds=self.kinds).since(Timestamp().now())
        self.client.subscribe([reqs_filter])
        self.client.handle_notifications(self.notification_handler_class(dvm=self))
        self.log.info(f"Listening for kinds: {self.kinds}")

    def listen_to_event(self, event_id: EventId):
        reqs_filter = Filter().event(event_id).since(Timestamp().now())
        self.client.subscribe([reqs_filter])
        self.client.handle_notifications(self.notification_handler_class(dvm=self))
        self.log.info(f"Listening for event: {event_id.to_bech32()}", extra={"hex": event_id.to_hex()})

    def run(self):
        # Implement the long-running task here
        self.log.info(f"DVM {self._name} started.")
        self.build_and_send_announcement()
        self.listen_to_kinds()

    def exit(self):
        # Implement cleanup or exit tasks here
        self.log.info(f"DVM {self._name} exiting.")

    def handle(self, relay_url, event):
        self.log.debug(f"handle event from {relay_url}", extra={"event": event.id(), "kind": event.kind()})

    def handle_msg(self, relay_url, msg):
        self.log.debug(f"handle_msg from {relay_url}", extra={"msg": msg})
