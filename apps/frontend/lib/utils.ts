import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges class names using clsx and tailwind-merge to avoid conflicts.
 *
 * @param inputs - Array of class values to merge.
 * @returns Concatenated and deduplicated class list string.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Formats a date string to a human-readable format.
 *
 * @param date - Date object or date string.
 * @returns Formatted date string (e.g. "May 25, 2026").
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Formats a currency value as USD (or Euro).
 *
 * @param value - Numerical currency value.
 * @returns Formatted currency string.
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}
