from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .adminforms import PostAdminForm
from .models import Post, Category, Tag
from typeidea.base_admin import BaseOwnerAdmin
from typeidea.custom_site import custom_site

# Register your models here.
class PostInline(admin.TabularInline): # 可选择继承自admin.StackedInline，以获取不同的展示样式
    fields = ('title', 'desc')
    extra = 1  # 控制额外多几个
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count')
    fields = ('name', 'status', 'is_nav')

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


class CategoryOwnerFilter(admin.SimpleListFilter):
    """ 自定义过滤器只展示当前用户分类 """

    title = '分类过滤器' # 展示标题
    parameter_name = 'owner_category' # 查询时URL参数的名字

    def lookups(self, request, model_admin): # 返回要展示的内容和查询用的id
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset): #根据URL Query的内容返回列表页数据
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = [  # 配置列表页面展示哪些字段
        'title', 'category', 'status',
        'created_time', 'owner', 'operator'
    ]
    list_display_links = [] # 配置哪些字段可以作为链接，点击它们，可以进入编辑页面

    list_filter = [CategoryOwnerFilter] # 配置页面过滤器，需要通过哪些字段来过滤列表页
    search_fields = ['title', 'category__name'] # 配置搜索字段

    actions_on_top = True # 动作相关的配置，是否展示在顶部
    actions_on_bottom = True # 动作相关的配置，是否展示在底部

    # 编辑页面
    save_on_top = True # 保存、编辑并新建按钮是否在顶部展示

    exclude = ('owner',) # 指定哪些字段是不展示的
    """
    fields = (
        ('category', 'title'),
        'desc',
        'status',
        'content',
        'tag',
    )
    """
    fieldsets = (                         # 控制布局，要求的格式是有两个元素的tuple的list
        ('基础配置', {                     # 板块名称
            'description': '基础配置描述',  # 描述、字段和样式配置
            'fields': (                  # fields:展示哪些元素
                ('title', 'category'),
                'status',
            ),
        } ),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('wide',),    # classes:给配置的版块加一些CSS属性
            'fields': ('tag',),
        })
    )
    # filter_horizontal = ('tag',)
    filter_vertical = ('tag', )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a',
            reverse('cus_admin:blog_post_change', args=(obj.id,)) # 指定表头的展示文案
        )
    operator.short_description = '操作'

    class Media:
        css = {
            'all': ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css",),
        }
        js = ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js', )


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user',
                    'change_message']