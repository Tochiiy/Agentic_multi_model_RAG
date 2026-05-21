import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  text: string;
}

export default function ConvertToMarkdown({ text }: Props) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // images
        img: ({ src, alt }) => (
          <img
            src={src}
            alt={alt}
            className="rounded-xl border border-white/10 my-4 shadow-lg max-w-full h-auto"
            loading="lazy"
          />
        ),

        // links
        a: ({ href, children }) => (
          <a
            href={href}
            className="text-blue-400 underline underline-offset-2 hover:text-blue-300"
            target="_blank"
            rel="noreferrer"
          >
            {children}
          </a>
        ),

        // lists
        ul: ({ ...props }) => (
          <ul className="list-disc list-inside space-y-1.5 mb-4 text-sm" {...props} />
        ),
        ol: ({ ...props }) => (
          <ol className="list-decimal list-inside space-y-1.5 mb-4 text-sm" {...props} />
        ),
        li: ({ ...props }) => (
          <li className="leading-relaxed" {...props} />
        ),

        // paragraphs
        p: ({ ...props }) => (
          <p className="mb-3 leading-relaxed text-sm" {...props} />
        ),

        // headings
        h1: ({ ...props }) => (
          <h1 className="text-xl font-bold mt-4 mb-2" {...props} />
        ),
        h2: ({ ...props }) => (
          <h2 className="text-lg font-semibold mt-3 mb-2" {...props} />
        ),
        h3: ({ ...props }) => (
          <h3 className="text-base font-semibold mt-2 mb-1" {...props} />
        ),

        // bold
        strong: ({ ...props }) => (
          <strong className="font-bold" {...props} />
        ),

        // inline + block code
        code: ({ className, children, ...props }) => {
          const isBlock = !!className;
          return isBlock ? (
            <code className={`${className} text-xs`} {...props}>
              {children}
            </code>
          ) : (
            <code
              className="px-1.5 py-0.5 rounded bg-black/20 text-blue-300 text-xs font-mono"
              {...props}
            >
              {children}
            </code>
          );
        },

        // code block wrapper
        pre: ({ ...props }) => (
          <pre
            className="p-4 rounded-xl overflow-x-auto bg-black/30 border border-white/10 mb-4 text-xs"
            {...props}
          />
        ),

        // tables
        table: ({ ...props }) => (
          <div className="overflow-x-auto mb-4">
            <table
              className="table-auto border-collapse border border-white/20 w-full text-xs"
              {...props}
            />
          </div>
        ),
        thead: ({ ...props }) => (
          <thead className="bg-white/10" {...props} />
        ),
        th: ({ ...props }) => (
          <th
            className="px-3 py-2 text-left font-semibold border border-white/20"
            {...props}
          />
        ),
        td: ({ ...props }) => (
          <td
            className="px-3 py-2 border border-white/10"
            {...props}
          />
        ),
        tr: ({ ...props }) => (
          <tr
            className="border-b border-white/10 hover:bg-white/5"
            {...props}
          />
        ),

        // blockquote
        blockquote: ({ ...props }) => (
          <blockquote
            className="border-l-4 border-blue-400 pl-4 italic text-sm opacity-80 my-3"
            {...props}
          />
        ),
      }}
    >
      {text}
    </ReactMarkdown>
  );
}