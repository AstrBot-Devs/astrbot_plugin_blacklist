from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import sp
from astrbot.api.message_components import At

@register("astrbot_plugin_blacklist", "大核桃", "黑名单插件，禁止用户和 AstrBot 交互，适用于 aiocqhttp, gewechat", "1.0.0", "https://github.com/AstrBot-Devs/astrbot_plugin_blacklist")
class BanPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.enable = config['enable']
        self.blacklist: dict = sp.get('blacklist', {})
        
        print(self.blacklist)

    def is_banned(self, event: AstrMessageEvent):
        """判断消息发送者是否被禁用"""
        if event.get_sender_id() in self.blacklist:
            return True
    
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def filter_banned_users(self, event: AstrMessageEvent):
        """全局事件过滤器：如果发送者被禁用，则停止事件传播，机器人不再响应该用户的消息。"""
        if not self.enable:
            return
        if self.is_banned(event):
            event.stop_event()  
            return

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban")
    async def ban_user(self, event: AstrMessageEvent):
        """禁用某个用户的使用权限。/ban @用户"""
        sender_id = event.get_sender_id()
        chain = event.message_obj.message
        ats = []
        are_u_ok = False
        for comp in chain:
            if isinstance(comp, At):
                if str(comp.qq) == str(sender_id):
                    are_u_ok = True
                    continue
                ats.append(str(comp.qq))
        if not ats:
            yield event.plain_result("请在 ban 后 @ 一个或者多个用户。")
            return
        for at in ats:
            if at not in self.blacklist:
                self.blacklist[at] = True
            
        sp.put('blacklist', self.blacklist)
        
        at_str = ", ".join([f"{at}" for at in ats])
        
        ret = f"已禁用 {at_str} 的使用权限。"
        if not self.enable:
            ret += "提示：当前黑名单功能未启用。输入 /ban_enable 临时启用。永久启用请在插件配置修改。"
        if not are_u_ok:
            ret += "忽略了对自己的ban..."
        yield event.plain_result(ret)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("pass")
    async def unban_user(self, event: AstrMessageEvent):
        """解除当前群聊中对指定用户的禁用。 /pass @用户"""

        chain = event.message_obj.message
        ats = []
        for comp in chain:
            if isinstance(comp, At):
                ats.append(str(comp.qq))
        if not ats:
            yield event.plain_result("请在 pass 后 @ 一个或者多个用户。")
            return
        for at in ats:
            if at in self.blacklist:
                del self.blacklist[at]
            
        sp.put('blacklist', self.blacklist)
        
        at_str = ", ".join([f"{at}" for at in ats])
        ret = f"已解除 {at_str} 的使用权限。"
        if not self.enable:
            ret += "提示：当前黑名单功能未启用。输入 /ban_enable 临时启用。永久启用请在插件配置修改。"
        yield event.plain_result(ret)
        
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban_enable")
    async def ban_enable(self, event: AstrMessageEvent):
        """启用黑名单功能。 /ban_enable"""
        self.enable = True
        yield event.plain_result("已临时启用黑名单功能，重启失效。永久启用请在插件配置修改。")
        
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ban_disable")
    async def ban_disable(self, event: AstrMessageEvent):
        """禁用黑名单功能。 /ban_disable"""
        self.enable = False
        yield event.plain_result("已禁用黑名单功能。重启失效。永久禁用请在插件配置修改。")
        
    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("banlist")
    async def list_banned_users(self, event: AstrMessageEvent):
        """列出所有被禁用的用户。 /banlist"""
        if not self.blacklist:
            yield event.plain_result("当前没有被禁用的用户。")
            return
        
        at_str = ", ".join([f"{user}" for user in self.blacklist.keys()])
        yield event.plain_result(f"被禁用的用户有: {at_str}")
