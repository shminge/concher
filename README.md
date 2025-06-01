# concher - python context switcher
Concher is a simple script that lets you set up contexts (apps and sites), group them, and launch as a group.
Commands:
- `register context|app|site name [url|path]` - adds an entry to the database (a path or url is not needed for contexts
- `add name context_name` - adds a registered item to a context
- `remove name [context_name]` - deletes an entry or context. If a context name is given, it removes the entry from the context
- `list [locations]` - if a second argument is given, it will list all entries, otherwise it will just list the contexts
- `open name` - opens a context, site or app. you can also just enter `name` and it will open.


