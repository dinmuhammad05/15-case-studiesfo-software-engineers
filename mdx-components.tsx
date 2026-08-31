import type { MDXComponents } from "mdx/types";
import * as Lesson from "@/components/lesson";

/**
 * MDX ichida import qilmasdan ishlatiladigan komponentlar.
 * Har bir dars .mdx faylida <Step>, <Arch>, <QA> ... to'g'ridan-to'g'ri yoziladi.
 */
export function useMDXComponents(components: MDXComponents): MDXComponents {
  return { ...Lesson, ...components };
}
