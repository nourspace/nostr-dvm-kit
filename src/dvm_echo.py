from nostr_sdk import EventBuilder, Event, Tag

from dvm import BaseDVM, BaseKinds, DefaultKinds


class Kinds(BaseKinds):
    KIND_5906_DVM_REMINDER_REQ = 5906
    KIND_6906_DVM_REMINDER_RES = 6906


# Todo (Nour): Do we really have to annotate the overrides?
class Echo(BaseDVM):
    name: str = 'dvm-echo'
    kinds: list[int] = [Kinds.KIND_5906_DVM_REMINDER_REQ]
    announcement_id: str = 'note1m4dg6gmyqmntz4h83zwk2plrz3pjtuh35szx4cf347vuag5g55dsy98xxs'
    # announcement_dict: AnnouncementDict = AnnouncementDict(
    #     name='dvm-echo',
    #     display_name='dvm-echo',
    #     about='Echo stuff for you',
    #     image='',
    #     picture='',
    # )

    confirmation_msg: str = "Are you sure you want me to echo? reply with yes"
    _db: dict = {}

    def handle(self, relay_url, event: Event):
        super().handle(relay_url, event)
        self.log.debug("Every day I'm handling...")

        # Respond to REQs
        if event.kind() == Kinds.KIND_5906_DVM_REMINDER_REQ:
            self.log.debug("Creating job", extra={"event_id": event.id().to_bech32()})
            tags = [
                Tag.parse(["e", event.id().to_hex(), "", "root"])
            ]
            builder = EventBuilder(kind=DefaultKinds.KIND_1_NOTE, content=self.confirmation_msg, tags=tags)
            event_id = self.client.send_event_builder(builder=builder)
            self.listen_to_event(event_id=event_id)
            self._db[event.id().to_hex()] = event
            self.log.info("Job created", extra={"event_id": event_id.to_bech32()})

        # Handle replies (later payments)
        elif event.kind() == DefaultKinds.KIND_1_NOTE:
            self.log.debug("Responding to job", extra={"event_id": event.id().to_bech32()})
            original_event_id = event.event_ids()[0]
            original_req = self._db[original_event_id.to_hex()]
            content = f"Echo: {original_req.content()}"
            tags = [
                Tag.parse(["e", original_event_id.to_hex(), "", "root"])
            ]
            builder = EventBuilder(kind=Kinds.KIND_6906_DVM_REMINDER_RES, content=content, tags=tags)
            event_id = self.client.send_event_builder(builder=builder)
            self.listen_to_event(event_id=event_id)
            self.log.info("Job done", extra={"event_id": event_id.to_bech32(), "orig": original_event_id.to_bech32()})
