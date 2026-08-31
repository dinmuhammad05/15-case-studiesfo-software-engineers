import createMDX from "@next/mdx";
import remarkGfm from "remark-gfm";

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath,
  trailingSlash: true,
  images: { unoptimized: true },
  pageExtensions: ["ts", "tsx", "mdx"],
};

export default createMDX({
  options: { remarkPlugins: [remarkGfm] },
})(nextConfig);
