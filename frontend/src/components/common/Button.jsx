/**
 * Button component - dark theme with indigo accent
 */

export function Button({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  className = '',
  ...props
}) {
  const base =
    variant === 'secondary' ? 'btn-secondary' :
    variant === 'ghost' ? 'btn-ghost' :
    'btn';

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${disabled ? 'opacity-40 cursor-not-allowed' : ''} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
