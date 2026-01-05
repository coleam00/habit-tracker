import clsx from 'clsx';

export function Card({ children, className = '' }) {
  return (
    <div className={clsx('bg-white rounded-lg shadow-md', className)}>
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ children, className = '' }) {
  return (
    <div className={clsx('px-4 py-3 border-b border-gray-100', className)}>
      {children}
    </div>
  );
};

Card.Body = function CardBody({ children, className = '' }) {
  return <div className={clsx('p-4', className)}>{children}</div>;
};
