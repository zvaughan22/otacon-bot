# otacon-bot/database/models.py

from tortoise import fields, models

class GuildSettings(models.Model):
    guild_id = fields.BigIntField(pk=True)
    prefix = fields.CharField(max_length=10, default=",")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "guild_settings"

class ReactionRoleMapping(models.Model):
    id = fields.IntField(pk=True)
    guild_id = fields.BigIntField()
    message_id = fields.BigIntField()
    emoji = fields.CharField(max_length=100)
    role_id = fields.BigIntField()

    class Meta:
        table = "reaction_roles"
        unique_together = ("message_id", "emoji")

    def __str__(self):
        return f"{self.guild_id} | {self.message_id} | {self.emoji} → {self.role_id}"
