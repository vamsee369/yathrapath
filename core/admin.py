from django.contrib import admin
from .models import Temple, Blog


@admin.register(Temple)
class TempleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'location', 'status')
    list_filter   = ('category', 'status')
    search_fields = ('name', 'location')

    BASE_FIELDSETS = [
        ('📍 Core Info', {
            'fields': ('name', 'location', 'description', 'image', 'latitude', 'longitude', 'status', 'category')
        }),
        ('🌍 Shared Details', {
            'fields': ('best_season', 'timings', 'mystery', 'rare_fact', 'quote'),
            'classes': ('collapse',),
        }),
    ]

    CATEGORY_FIELDSETS = {
        'temple': [
            ('🛕 Temple Details', {
                'fields': ('deity', 'dynasty', 'history', 'architecture', 'science_fact'),
            }),
            ('🎉 Culture & Rituals', {
                'fields': ('festivals', 'rituals'),
                'classes': ('collapse',),
            }),
        ],
        'heritage': [
            ('🏛 Heritage Details', {
                'fields': ('dynasty', 'history', 'architecture', 'science_fact'),
            }),
        ],
        'mountain': [
            ('⛰ Mountain Details', {
                'fields': ('altitude', 'trek_difficulty', 'trek_duration', 'viewpoints', 'flora_fauna'),
            }),
        ],
        'beach': [
            ('🏖 Beach Details', {
                'fields': ('beach_type', 'water_activity', 'tide_info', 'nearby_stays', 'sunset_sunrise'),
            }),
        ],
        'scenic': [
            ('🌿 Scenic / Nature Details', {
                'fields': ('landscape_type', 'wildlife', 'flora_fauna', 'entry_info', 'sunset_sunrise'),
            }),
        ],
        'other': [
            ('📋 Additional Info', {
                'fields': ('landscape_type', 'entry_info'),
                'classes': ('collapse',),
            }),
        ],
    }

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.BASE_FIELDSETS + [
                ('🛕 Temple / Religious', {
                    'fields': ('deity', 'dynasty', 'history', 'architecture', 'science_fact', 'festivals', 'rituals'),
                    'classes': ('collapse',),
                }),
                ('⛰ Mountain / Hill', {
                    'fields': ('altitude', 'trek_difficulty', 'trek_duration', 'viewpoints'),
                    'classes': ('collapse',),
                }),
                ('🏖 Beach / Coastal', {
                    'fields': ('beach_type', 'water_activity', 'tide_info', 'nearby_stays'),
                    'classes': ('collapse',),
                }),
                ('🌿 Scenic / Nature', {
                    'fields': ('landscape_type', 'wildlife', 'flora_fauna', 'entry_info'),
                    'classes': ('collapse',),
                }),
                ('🌅 Sunrise / Sunset', {
                    'fields': ('sunset_sunrise',),
                    'classes': ('collapse',),
                }),
            ]
        category = obj.category
        extra = self.CATEGORY_FIELDSETS.get(category, [])
        return self.BASE_FIELDSETS + extra


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display    = ('title', 'created_at', 'views', 'reading_time')
    list_filter     = ('created_at',)
    search_fields   = ('title',)
    readonly_fields = ('views', 'reading_time')

    fieldsets = [
        ('📝 Core', {
            'fields': ('title', 'image', 'image_caption', 'created_at'),
        }),
        ('📊 Stats (auto)', {
            'fields': ('views', 'reading_time'),
            'classes': ('collapse',),
        }),
        ('✍️ Rich Content', {
            'fields': ('intro', 'experience', 'highlights'),
        }),
        ('🧭 Travel Info', {
            'fields': ('best_time', 'how_to_reach', 'food_stay', 'travel_tips'),
            'classes': ('collapse',),
        }),
        ('💬 Closing', {
            'fields': ('closing_thought',),
            'classes': ('collapse',),
        }),
        ('🗂 Legacy Content', {
            'fields': ('content',),
            'classes': ('collapse',),
            'description': 'Old content field — only used if rich fields above are empty.',
        }),
    ]
