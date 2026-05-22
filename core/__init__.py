from .scraper import UniversalScraper


def scrape_urls(
    urls: list,
    output_dir: str = './scraped_content',
    delay: float = 1.5,
    force_rescrape: bool = False,
    verbose: bool = False,
) -> dict:
    """Programmatic API — URL list in, summary dict out.

    Intended for use by AI agents and other programs.
    Returns: {total, successful, failed, output_dir, index_path}
    """
    scraper = UniversalScraper(
        output_dir=output_dir,
        delay=delay,
        force_rescrape=force_rescrape,
        verbose=verbose,
    )
    return scraper.scrape_urls(urls)
