/**
 * Input component
 */
export function Input({
  label,
  value,
  onChange,
  type = 'text',
  placeholder = '',
  className = '',
  ...props
}) {
  return (
    <div className={className}>
      {label && <label className="label">{label}</label>}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="input"
        {...props}
      />
    </div>
  );
}

/**
 * Select component
 */
export function Select({
  label,
  value,
  onChange,
  options,
  className = '',
  ...props
}) {
  return (
    <div className={className}>
      {label && <label className="label">{label}</label>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input"
        {...props}
      >
        {options.map((option) => (
          <option
            key={typeof option === 'object' ? option.value : option}
            value={typeof option === 'object' ? option.value : option}
          >
            {typeof option === 'object' ? option.label : option}
          </option>
        ))}
      </select>
    </div>
  );
}
