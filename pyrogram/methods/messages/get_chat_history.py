#  Pyrofork - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2022-present Mayuri-Chan <https://github.com/Mayuri-Chan>
#
#  This file is part of Pyrofork.
#
#  Pyrofork is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrofork is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrofork.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from typing import Union, Optional, AsyncGenerator

import pyrogram
from pyrogram import types, raw, utils


async def get_chunk(
    *,
    client: "pyrogram.Client",
    chat_id: Union[int, str],
    limit: int = 0,
    offset: int = 0,
    from_message_id: int = 0,
    from_date: datetime = utils.zero_datetime(),
    min_id: int = 0,
    max_id: int = 0,
    reverse: Optional[bool] = None
):
    messages = await client.invoke(
        raw.functions.messages.GetHistory(
            peer=await client.resolve_peer(chat_id),
            offset_id=from_message_id,
            offset_date=utils.datetime_to_timestamp(from_date),
            add_offset=offset,
            limit=limit,
            max_id=max_id,
            min_id=min_id,
            hash=0
        ),
        sleep_threshold=60
    )
    if reverse:
        messages.messages.reverse()

    return await utils.parse_messages(client, messages, replies=0)


class GetChatHistory:
    async def get_chat_history(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0,
        offset: int = 0,
        offset_id: int = 0,
        offset_date: datetime = utils.zero_datetime(),
        min_id: int = 0,
        max_id: int = 0,
        reverse: Optional[bool] = None
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Get messages from a chat history.

        The messages are returned in reverse chronological order.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                You can also use chat public link in form of *t.me/<username>* (str).

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, no limit is applied and all messages are returned.

            offset (``int``, *optional*):
                Sequential number of the first message to be returned..
                Negative values are also accepted and become useful in case you set offset_id or offset_date.

            offset_id (``int``, *optional*):
                Identifier of the first message to be returned.

            offset_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date as offset to retrieve only older messages starting from that date.

            min_id: (``int``, *optional*):
                The minimum message id. you will not get any message which have id smaller than min_id.

            max_id: (``int``, *optional*):
                The maximum message id. you will not get any message which have id greater than max_id.

            reverse (``bool``, *optional*):
                Pass True to retrieve the messages in reversed order (from older to most recent).

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.

        Example:
            .. code-block:: python

                async for message in app.get_chat_history(chat_id):
                    print(message.text)
        """
        current = 0
        total = limit or (1 << 31) - 1
        limit = min(100, total)

        while True:
            messages = await get_chunk(
                client=self,
                chat_id=chat_id,
                limit=limit,
                offset=offset,
                from_message_id=offset_id,
                from_date=offset_date,
                min_id=min_id,
                max_id=max_id,
                reverse=reverse
            )

            if not messages:
                return

            offset_id = messages[-1].id

            for message in messages:
                yield message

                current += 1

                if current >= total:
                    return
