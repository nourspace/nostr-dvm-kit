import json
import logging
import time
from environs import Env

from nostr_sdk import (
    Client,
    ClientSigner,
    EventBuilder,
    Filter,
    HandleNotification,
    init_logger,
    Keys,
    LogLevel,
    Metadata,
    Tag,
    Timestamp,
)

from config import env, DEFAULT_RELAYS


def get_client(account: str) -> Client:
    # load keys
    keys = Keys.from_sk_str(account)

    # initialize with Keys signer
    signer = ClientSigner.keys(keys)
    client = Client(signer)

    # Add multiple relays
    client.add_relays(env.list("NOSTR_RELAYS", default=DEFAULT_RELAYS))

    # Connect
    client.connect()

    return client


def text_note(client, text, tags=None):
    if not tags:
        tags = []
    builder = EventBuilder.text_note(text, tags)
    return client.send_event_builder(builder)


def set_metadata(client, metadata):
    metadata = Metadata.from_json(json.dumps(metadata))
    client.set_metadata(metadata)
