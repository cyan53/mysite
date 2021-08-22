from django.contrib import admin


class BaseOwnerAdmin(admin.ModelAdmin):
    """
    1. 用来自动补充文章、分类、标签、侧边栏、友链这些Model的owner字段
    2. 用来针对queryset过滤当前用户的数据
    """
    exclude = ('owner', )

    def get_queryset(self, request):
        qs = super(BaseOwnerAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        # obj当前要保存的对象；form页面提交过来的表单之后的对象；
        # change标志本次保存的数据是新增的还是更新的
        obj.owner = request.user
        # 自动设置owner
        return super(BaseOwnerAdmin, self).save_model(request, obj, form, change)