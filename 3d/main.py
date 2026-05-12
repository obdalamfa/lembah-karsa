import sys
import logging
from game.app import run

# Setup logging dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Memulai Lembah Karsa 3D...")
    try:
        run()
    except Exception as e:
        logging.error(f"Game crash! Terjadi kesalahan fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
