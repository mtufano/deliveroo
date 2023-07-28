import os
from deliveroo_crawler.deliveroo_crawler_wip import DeliverooCrawler

source_directory = 'url_collector/data/boroughs_london'
data_path = 'crawled_data'
deliveroo_links = []

for filename in os.listdir(source_directory):
    if filename.endswith('_urls.txt'):
        # Remove the "_urls.txt" part from the filename
        file_part = filename[:-9]  # Remove the last 9 characters from the filename

        file_path = os.path.join(source_directory, filename)
        # Create a new directory for the file_part if it doesn't exist
        end_dir = os.path.join(data_path, file_part)
        if not os.path.exists(end_dir):
            os.makedirs(end_dir)

        with open(file_path, 'r') as file:
            for line in file:

                # Add the line to the deliveroo_links list along with the modified filename
                deliveroo_links.append((line, end_dir))

if __name__ == '__main__':
    for link, end_dir in deliveroo_links:
        # Modify the code according to your needs
        dc = DeliverooCrawler(link, end_dir)
        dc.write_to_csv()