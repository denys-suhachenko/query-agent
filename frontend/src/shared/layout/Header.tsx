export function Header({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <header className="bg-primary relative z-50 shadow-md">{children}</header>
  );
}
