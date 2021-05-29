from tortoise import fields, models


class Bot(models.Model):
    class Meta:
        table = "bots"

    id = fields.BigIntField(pk=True)
    bot_id = fields.BigIntField()
    user_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    start_time = fields.DatetimeField()
    off_time = fields.DatetimeField()
    dm = fields.BooleanField(default=False)
    log_channel_id = fields.BigIntField()
    history: fields.ManyToManyRelation["History"] = fields.ManyToManyField("models.History")


class History(models.Model):
    class Meta:
        table = "history"

    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
