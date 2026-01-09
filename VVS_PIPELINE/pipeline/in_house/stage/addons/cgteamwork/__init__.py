from .version import __version__

__all__ = (
    "__version__"
)

# docker run --init -ti --rm -p 8090:80 --name cgwire -v zou-storage:/var/lib/postgresql -v zou-storage:/opt/zou/previews cgwire/cgwire
# admin@example.com
# mysecretpassword