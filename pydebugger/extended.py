from cleaner import DebugCleaner
import sys

class ExtendedCleaner(DebugCleaner):
    def usage(self):
        parser = super().usage()  # ✅ Sekarang ini valid
        ext_group = parser.add_argument_group("Extended Options")
        ext_group.add_argument("--extra", action="store_true", help="Enable extra processing")
        ext_group.add_argument("--log", type=str, help="Write log output to file")

        if len(sys.argv) == 1:
            parser.print_help()
            return parser

        args = parser.parse_args()
        if args.log:
            print("log ........")
        elif args.extra:
            print("extra ...........")

        return parser

if __name__ == '__main__':
    ExtendedCleaner().usage()