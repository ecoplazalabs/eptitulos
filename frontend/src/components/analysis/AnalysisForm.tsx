import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Alert from '@/components/ui/Alert';
import { useCreateAnalysis } from '@/hooks/useCreateAnalysis';
import { OFICINAS_REGISTRALES } from '@/lib/constants';

interface FormValues {
  oficina: string;
  partida: string;
}

interface FormErrors {
  oficina?: string;
  partida?: string;
}

function validate(values: FormValues): FormErrors {
  const errors: FormErrors = {};

  if (!values.oficina) {
    errors.oficina = 'Selecciona una oficina registral';
  }

  if (!values.partida) {
    errors.partida = 'Ingresa el numero de partida';
  } else if (!/^\d+$/.test(values.partida)) {
    errors.partida = 'La partida solo debe contener numeros';
  } else if (values.partida.length < 6 || values.partida.length > 12) {
    errors.partida = 'La partida debe tener entre 6 y 12 digitos';
  }

  return errors;
}

export default function AnalysisForm() {
  const navigate = useNavigate();
  const { mutate, isPending, error } = useCreateAnalysis();

  const [values, setValues] = useState<FormValues>({ oficina: '', partida: '' });
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const getApiErrorMessage = (): string | null => {
    if (!error) return null;

    const axiosError = error as { response?: { status?: number; data?: { error?: { message?: string } } } };
    const status = axiosError.response?.status;

    if (status === 409) {
      return 'Ya existe un analisis en progreso para esta partida. Espera a que termine antes de solicitar uno nuevo.';
    }

    const message = axiosError.response?.data?.error?.message;
    return message ?? 'Ocurrio un error al procesar la solicitud. Intenta de nuevo.';
  };

  const handleBlur = (field: keyof FormValues) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const fieldErrors = validate(values);
    setErrors((prev) => ({ ...prev, [field]: fieldErrors[field] }));
  };

  const handleChange = (field: keyof FormValues, value: string) => {
    const next = { ...values, [field]: value };
    setValues(next);

    if (touched[field]) {
      const fieldErrors = validate(next);
      setErrors((prev) => ({ ...prev, [field]: fieldErrors[field] }));
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    setTouched({ oficina: true, partida: true });
    const formErrors = validate(values);
    setErrors(formErrors);

    if (Object.keys(formErrors).length > 0) return;

    mutate(
      { oficina: values.oficina, partida: values.partida },
      {
        onSuccess: (data) => {
          void navigate(`/analyses/${data.id}`);
        },
      },
    );
  };

  const apiErrorMessage = getApiErrorMessage();

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
      {apiErrorMessage && (
        <Alert variant="error" title="Error al solicitar analisis">
          {apiErrorMessage}
        </Alert>
      )}

      <Select
        id="oficina"
        label="Oficina Registral"
        placeholder="Selecciona una oficina"
        options={OFICINAS_REGISTRALES.map((o) => ({ value: o.value, label: o.label }))}
        value={values.oficina}
        error={touched.oficina ? errors.oficina : undefined}
        onChange={(e) => handleChange('oficina', e.target.value)}
        onBlur={() => handleBlur('oficina')}
        disabled={isPending}
      />

      <Input
        id="partida"
        label="Numero de Partida"
        placeholder="Ej. 12345678"
        inputMode="numeric"
        pattern="[0-9]*"
        maxLength={12}
        value={values.partida}
        error={touched.partida ? errors.partida : undefined}
        onChange={(e) => handleChange('partida', e.target.value)}
        onBlur={() => handleBlur('partida')}
        disabled={isPending}
      />

      <Button type="submit" loading={isPending} fullWidth size="lg" className="mt-1">
        Analizar Partida
      </Button>
    </form>
  );
}
