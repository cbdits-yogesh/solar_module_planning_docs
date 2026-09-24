'''
Reference Document Type: Raven Message
DocType Event: After Insert
'''

SOURCE_CHANNEL = "Raven-sadbhav"
BOT_NAME = "Sadbhav Bot"

# 1. Ensure we are in the correct channel
channel_id = doc.get("channel") or doc.get("channel_id")
if channel_id != SOURCE_CHANNEL:
    # If not the target channel, stop execution
    pass
elif doc.get("is_bot_message"):
    # 2. Prevent infinite loops by ignoring bot messages
    pass
else:
    # 3. Safely extract message content and strip HTML tags so it renders correctly
    raw_content = doc.get("text") or doc.get("content") or ""
    try:
        msg_content = frappe.utils.strip_html(raw_content).strip()
    except Exception:
        # Fallback if strip_html is not available
        import re
        msg_content = re.sub('<[^<]+>', '', raw_content).strip()
        
    sender = doc.owner

    # 4. Safely extract mentions
    mentions = doc.get("mentions", [])
    target_users = []
    
    if isinstance(mentions, str):
        import json
        try:
            mentions = json.loads(mentions)
        except Exception:
            mentions = []
            
    for m in mentions:
        u = None
        if isinstance(m, dict):
            u = m.get("user") or m.get("user_id")
        else:
            # 'm' is a Frappe document (e.g. RavenMention), so .get() is safe and doesn't need hasattr
            u = m.get("user") or m.get("user_id")
            
        if u:
            target_users.append(u)

    # 5. Helper function for DM channel
    def get_or_create_dm_channel(user1, user2):
        try:
            # Figure out the exact field names used in this Raven version
            member_meta = frappe.get_meta("Raven Channel Member")
            user_field = "user" if member_meta.has_field("user") else "user_id"
            
            if member_meta.istable:
                channel_field = "parent"
            else:
                channel_field = "channel" if member_meta.has_field("channel") else "channel_id"

            # 1. Find existing DM channel
            channels_u1 = frappe.get_all("Raven Channel Member", filters={user_field: user1}, fields=[channel_field])
            channels_u2 = frappe.get_all("Raven Channel Member", filters={user_field: user2}, fields=[channel_field])
            
            c1 = set([d.get(channel_field) for d in channels_u1])
            c2 = set([d.get(channel_field) for d in channels_u2])
            common = c1.intersection(c2)
            
            if common:
                dms = frappe.get_all("Raven Channel", filters={"name": ("in", list(common)), "is_direct_message": 1})
                if dms:
                    return dms[0].name
                    
            # 2. Create if not found
            ch = frappe.new_doc("Raven Channel")
            ch.is_direct_message = 1
            # channel_name is mandatory and must be a valid User (Link field)
            if ch.meta.has_field("channel_name"):
                ch.channel_name = user2
            ch.insert(ignore_permissions=True)
            
            # 3. Add Members Safely (Raven might auto-add members on insert)
            ch.reload()
            existing_members = []
            if member_meta.istable:
                existing_members = [m.get(user_field) for m in ch.get("members", [])]
            else:
                docs = frappe.get_all("Raven Channel Member", filters={channel_field: ch.name}, fields=[user_field])
                existing_members = [d.get(user_field) for d in docs]
                
            needs_save = False
            for u in [user1, user2]:
                if u not in existing_members:
                    if member_meta.istable:
                        ch.append("members", {user_field: u})
                        needs_save = True
                    else:
                        try:
                            frappe.get_doc({
                                "doctype": "Raven Channel Member",
                                channel_field: ch.name,
                                user_field: u
                            }).insert(ignore_permissions=True)
                        except Exception:
                            pass
                            
            if member_meta.istable and needs_save:
                try:
                    ch.save(ignore_permissions=True)
                except Exception as e:
                    # Ignore 'already a member' errors as Raven might have handled it
                    if "already a member" not in str(e).lower():
                        frappe.log_error(f"Error saving members: {str(e)}", "Mention Bot Error")
                
            return ch.name
        except Exception as e:
            frappe.log_error(f"Error creating DM channel: {str(e)}", "Mention Bot Error")
            return None

    # 6. Process each mentioned user
    for target_user in target_users:
        if not target_user or target_user == sender:
            continue
            
        dm_channel = get_or_create_dm_channel(sender, target_user)
        
        if dm_channel:
            bot_text = f"**{sender}** You got a message from them. {channel_id}:\n\n{msg_content}"
            
            try:
                # Use Raven's built-in API to send the message properly (this handles tip-tap json & websockets)
                send_message = frappe.get_attr("raven.api.raven_message.send_message")
                
                json_payload = {
                    "type": "doc",
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": bot_text}]}]
                }
                
                # We call send_message. If it returns the doc, we can update the bot flags.
                msg_doc = send_message(
                    channel_id=dm_channel,
                    text=bot_text,
                    json_content=json_payload
                )
                
                # Fetch the message to mark it as a bot message
                if msg_doc and hasattr(msg_doc, "name"):
                    msg_name = msg_doc.name
                else:
                    # In case send_message doesn't return the doc, fetch latest
                    latest = frappe.db.sql("SELECT name FROM `tabRaven Message` WHERE channel=%s OR channel_id=%s ORDER BY creation DESC LIMIT 1", (dm_channel, dm_channel))
                    msg_name = latest[0][0] if latest else None
                    
                if msg_name:
                    frappe.db.set_value("Raven Message", msg_name, {
                        "is_bot_message": 1,
                        "bot": BOT_NAME
                    })
            except Exception as e:
                frappe.log_error(f"Raven API Error: {str(e)}", "Mention Bot Error")
                # Fallback if the API fails
                bot_msg = frappe.new_doc("Raven Message")
                if bot_msg.meta.has_field("channel"):
                    bot_msg.channel = dm_channel
                else:
                    bot_msg.channel_id = dm_channel
                    
                bot_msg.text = bot_text
                if bot_msg.meta.has_field("content"):
                    bot_msg.content = bot_text
                    
                if bot_msg.meta.has_field("json_content"):
                    import json
                    bot_msg.json_content = json.dumps(json_payload)
                
                bot_msg.is_bot_message = 1
                bot_msg.bot = BOT_NAME
                bot_msg.insert(ignore_permissions=True)

