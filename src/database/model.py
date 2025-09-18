from tortoise.models import Model
from tortoise import fields


class BaseModel(Model):
    @classmethod
    def get_(cls, *args, **kwargs):
        super().get(*args, **kwargs)

    @classmethod
    def get(cls, **kwargs):
        return cls.filter(**kwargs)

    @classmethod
    async def add(cls, **kwargs):
        pk_name = cls.describe()["pk_field"]["name"]
        if pk_name == "id" and pk_name not in kwargs:
            filters = kwargs
        else:
            filters = {pk_name: kwargs[pk_name]}
        if await cls.get(**filters).exists():
            return False
        await cls.create(**kwargs)
        return True

    @classmethod
    async def delete(cls, **kwargs):
        query = cls.get(**kwargs)
        if await query.exists():
            await query.delete()
            return True
        return False

    @classmethod
    async def update(cls, q, **kwargs):
        query = cls.get(**q)
        if await query.exists():
            await query.update(**kwargs)
            return True
        return False

    @classmethod
    async def update_by_pk(cls, pk, **kwargs):
        return await cls.filter(id=pk).update(kwargs)

    class Meta:
        abstract = True


class BiliCredential(BaseModel):
    id = fields.BigIntField(primary_key=True, generated=True)
    sessdata = fields.CharField(max_length=500, null=True)
    bili_jct = fields.CharField(max_length=500, null=True)
    buvid3 = fields.CharField(max_length=500, null=True)
    buvid4 = fields.CharField(max_length=500, null=True)
    dedeuserid = fields.CharField(max_length=500, null=True)
    ac_time_value = fields.CharField(max_length=500, null=True)
    uid = fields.BigIntField()
    enable = fields.BooleanField()


class BiliConfig(BaseModel):
    id = fields.BigIntField(primary_key=True, generated=True)
    room_id = fields.BigIntField()
    modal_level = fields.IntField()
    user_level = fields.IntField()
    sing_prefix = fields.CharField(max_length=100)
    sing_cd = fields.IntField()


class DyConfig(BaseModel):
    id = fields.BigIntField(primary_key=True, generated=True)
    room_id = fields.BigIntField()
    sing_prefix = fields.CharField(max_length=100)
    sing_cd = fields.IntField()


def ignore_none(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}
