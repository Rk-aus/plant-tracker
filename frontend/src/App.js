import { useEffect, useState } from 'react';
import { translateToJa } from './utils/translate';

function App() {
  const [plants, setPlants] = useState([]);
  const [formData, setFormData] = useState({
    plant_name_en: '',
    plant_class_en: '',
    plant_name_ja: '',
    plant_class_ja: '',
    plant_date: '',
    botanical_name: '',
    location: '',
    image_path: null,
  });

  const [message, setMessage] = useState({ type: '', text: '' });
  const [submitting, setSubmitting] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({
    plant_id: null,
    plant_name_en: '',
    plant_class_en: '',
    plant_name_ja: '',
    plant_class_ja: '',
    plant_date: '',
    botanical_name: '',
    location: '',
    image_path: null,
  });

  const [searchQuery, setSearchQuery] = useState('');
  const [language, setLanguage] = useState('en');

  const [sortByDate, setSortByDate] = useState(false);

  const labels = {
    en: {
      title: '🌿 My Plant Tracker',
      lang_en: 'EN',
      lang_ja: 'JA',
      addMessage: '✅ Plant added successfully!',
      addFailedMessage: '❌ Failed to add plant.',
      updateMessage: '✏️ Plant updated successfully!',
      updateFailedMessage: '❌ Failed to update plant.',
      deletedMessage: '🗑️ Plant deleted successfully!',
      deleteFailedMessage: '❌ Failed to delete plant.',
      name: 'Name',
      class: 'Class',
      date: 'Date (optional)',
      location: 'Location',
      image_path: 'Image',
      botanical_name: 'Botanical Name',
      add: 'Add Plant',
      defaultOrder: 'Default Order',
      newestFirst: 'Newest First',
      edit: 'Edit',
      delete: 'Delete',
      search: '🔍 Search plants by name or class...',
      cancel: 'Cancel',
      save: 'Save',
      editModal: 'Edit Plant',
    },
    ja: {
      title: '🌿 植物リスト',
      lang_en: '英',
      lang_ja: '日',
      addMessage: '✅ 植物が追加されました！',
      addFailedMessage: '❌ 植物を追加することができませんでした。',
      updateMessage: '✏️ 植物が更新されました！',
      updateFailedMessage: '❌ 植物を更新することができませんでした。',
      deletedMessage: '🗑️ 植物が削除されました！',
      deleteFailedMessage: '❌ 植物を削除することができませんでした。',
      name: '名前',
      class: '分類',
      date: '日付（任意）',
      location: '場所',
      botanical_name: '学名',
      image_path: '画像',
      add: '植物を追加',
      defaultOrder: '追加順',
      newestFirst: '新しい順',
      edit: '編集',
      delete: '削除',
      search: '🔍 植物名や分類で検索...',
      cancel: 'キャンセル',
      save: '保存',
      editModal: '植物を編集',
    },
  };

  const fetchAndUpdatePlants = async (sort = false, lang = 'en') => {
    const url = sort
      ? `${process.env.REACT_APP_API_URL}/plants/sort_by_date`
      : `${process.env.REACT_APP_API_URL}/plants`;

    try {
      const res = await fetch(url);
      const data = await res.json();

      if (lang === 'ja') {
        const translated = await Promise.all(
          data.map(async (p) => {
            if (p.location) {
              p.location_ja = await translateToJa(p.location);
            }
            return p;
          })
        );
        setPlants(translated);
      } else {
        setPlants(data);
      }
    } catch (err) {
      console.error('Error fetching plants:', err);
    }
  };

  useEffect(() => {
    fetchAndUpdatePlants(sortByDate, language);
  }, [sortByDate, language]);

  const validateAdd = () => {
    if (!formData.plant_name_en.trim()) {
      return (
        setMessage({ type: 'error', text: 'English name is required.' }) ||
        false
      );
    }
    if (!formData.plant_class_en.trim()) {
      return (
        setMessage({ type: 'error', text: 'English class is required.' }) ||
        false
      );
    }
    if (!formData.plant_name_ja.trim()) {
      return (
        setMessage({ type: 'error', text: 'Japanese name is required.' }) ||
        false
      );
    }
    if (!formData.plant_class_ja.trim()) {
      return (
        setMessage({ type: 'error', text: 'Japanese class is required.' }) ||
        false
      );
    }
    if (!formData.botanical_name.trim()) {
      return (
        setMessage({ type: 'error', text: 'Botanical name is required.' }) ||
        false
      );
    }
    if (!formData.location.trim()) {
      return (
        setMessage({ type: 'error', text: 'Location is required.' }) || false
      );
    }
    if (!formData.image_path) {
      return setMessage({ type: 'error', text: 'Image is required.' }) || false;
    }
    return true;
  };

  const validateEdit = () => {
    const en = language === 'en';
    if (en && !editFormData.plant_name_en.trim()) {
      return (
        setMessage({ type: 'error', text: 'English name is required.' }) ||
        false
      );
    }
    if (en && !editFormData.plant_class_en.trim()) {
      return (
        setMessage({ type: 'error', text: 'English class is required.' }) ||
        false
      );
    }
    if (!en && !editFormData.plant_name_ja.trim()) {
      return (
        setMessage({ type: 'error', text: 'Japanese name is required.' }) ||
        false
      );
    }
    if (!en && !editFormData.plant_class_ja.trim()) {
      return (
        setMessage({ type: 'error', text: 'Japanese class is required.' }) ||
        false
      );
    }
    if (!editFormData.botanical_name.trim()) {
      return (
        setMessage({ type: 'error', text: 'Botanical name is required.' }) ||
        false
      );
    }

    if (!editFormData.location.trim()) {
      return (
        setMessage({ type: 'error', text: 'Location is required.' }) || false
      );
    }

    if (!editFormData.image_path) {
      return setMessage({ type: 'error', text: 'Image is required.' }) || false;
    }

    if (
      editFormData.plant_date &&
      !/^\d{4}-\d{2}-\d{2}$/.test(editFormData.plant_date)
    ) {
      return (
        setMessage({
          type: 'error',
          text: 'Invalid date format (YYYY-MM-DD).',
        }) || false
      );
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateAdd()) {
      return;
    }

    setSubmitting(true);

    const data = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (value) {
        data.append(key, value);
      }
    });

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/plants`, {
        method: 'POST',
        headers: {
          'x-api-key': process.env.REACT_APP_API_KEY,
        },
        body: data,
      });

      if (!res.ok) {
        throw new Error('Failed to add plant');
      }

      setFormData({
        plant_name_en: '',
        plant_class_en: '',
        plant_name_ja: '',
        plant_class_ja: '',
        botanical_name: '',
        location: '',
        plant_date: '',
        image_path: null,
      });

      setMessage({ type: 'success', text: labels[language].addMessage });
      fetchAndUpdatePlants(sortByDate);
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: labels[language].addFailedMessage });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/plants/${id}`, {
        method: 'DELETE',
        headers: {
          'x-api-key': process.env.REACT_APP_API_KEY,
        },
      });
      if (!res.ok) {
        throw new Error();
      }
      setMessage({ type: 'success', text: labels[language].deletedMessage });
      await fetchAndUpdatePlants();
    } catch {
      setMessage({ type: 'error', text: labels[language].deleteFailedMessage });
    }
  };

  const handleEditClick = (plant) => {
    setEditFormData({
      plant_id: plant.plant_id,
      plant_name_en: plant.plant_name_en || '',
      plant_class_en: plant.plant_class_en || '',
      plant_name_ja: plant.plant_name_ja || '',
      plant_class_ja: plant.plant_class_ja || '',
      plant_date: plant.plant_date
        ? new Date(plant.plant_date).toISOString().split('T')[0]
        : '',
      botanical_name: plant.botanical_name || '',
      location: plant.location || '',
      image_path: null,
    });
    setIsModalOpen(true);
  };

  const handleEditSave = async () => {
    if (!validateEdit()) {
      return;
    }

    const form = new FormData();
    form.append('plant_name_en', editFormData.plant_name_en);
    form.append('plant_class_en', editFormData.plant_class_en);
    form.append('plant_name_ja', editFormData.plant_name_ja);
    form.append('plant_class_ja', editFormData.plant_class_ja);
    form.append('botanical_name', editFormData.botanical_name);
    form.append('location', editFormData.location);
    form.append('image_path', editFormData.image_path);
    if (editFormData.plant_date) {
      form.append('plant_date', editFormData.plant_date);
    }

    try {
      const res = await fetch(
        `${process.env.REACT_APP_API_URL}/plants/${editFormData.plant_id}`,
        {
          method: 'PUT',
          headers: {
            'x-api-key': process.env.REACT_APP_API_KEY,
          },
          body: form,
        }
      );

      if (!res.ok) {
        throw new Error();
      }

      await fetchAndUpdatePlants();
      setIsModalOpen(false);
      setMessage({ type: 'success', text: labels[language].updateMessage });
    } catch {
      setMessage({ type: 'error', text: labels[language].updateFailedMessage });
    }
  };

  const filteredPlants = plants.filter((plant) => {
    return (
      plant[`plant_name_${language}`]
        ?.toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
      plant[`plant_class_${language}`]
        ?.toLowerCase()
        .includes(searchQuery.toLowerCase())
    );
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-100 to-green-300 p-6">
      <div className="max-w-xl mx-auto bg-white rounded-xl shadow-md p-8">
        <h1 className="text-3xl font-bold mb-6 text-center text-green-800">
          {labels[language].title}
        </h1>

        <nav className="flex justify-end mb-4">
          <button
            onClick={() => {
              setLanguage((prev) => (prev === 'en' ? 'ja' : 'en'));
              setMessage({ type: '', text: '' });
            }}
            aria-label={`Switch language to ${language === 'en' ? 'Japanese' : 'English'}`}
            className="text-sm font-medium text-green-700 underline hover:text-green-900 focus:outline-none focus:ring-2 focus:ring-green-500 rounded"
          >
            {language === 'en' ? '🇯🇵 日本語へ' : '🇺🇸 Switch to English'}
          </button>
        </nav>

        {message.text && (
          <div
            className={`mb-6 p-3 rounded ${
              message.type === 'success'
                ? 'bg-green-100 text-green-800 border border-green-300'
                : 'bg-red-100 text-red-800 border border-red-300'
            }`}
          >
            {message.text}
          </div>
        )}

        <form
          data-testid="add-form"
          onSubmit={handleSubmit}
          className="space-y-4 mb-8"
        >
          <div className="mb-4">
            <label
              htmlFor="plant_name_en"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].name} (${labels[language].lang_en})`}
            </label>
            <input
              id="plant_name_en"
              type="text"
              value={formData.plant_name_en ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, plant_name_en: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="plant_class_en"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].class} (${labels[language].lang_en})`}
            </label>
            <input
              id="plant_class_en"
              type="text"
              value={formData.plant_class_en ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, plant_class_en: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="plant_name_ja"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].name} (${labels[language].lang_ja})`}
            </label>
            <input
              id="plant_name_ja"
              type="text"
              value={formData.plant_name_ja ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, plant_name_ja: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="plant_class_ja"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].class} (${labels[language].lang_ja})`}
            </label>
            <input
              id="plant_class_ja"
              type="text"
              value={formData.plant_class_ja ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, plant_class_ja: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="location"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].location}`}
            </label>
            <input
              id="location"
              type="text"
              value={formData.location ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, location: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="botanical_name"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].botanical_name}`}
            </label>
            <input
              id="botanical_name"
              type="text"
              value={formData.botanical_name ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, botanical_name: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="image"
              className="block text-green-700 font-semibold"
            >
              {`${labels[language].image_path}`}
            </label>
            <input
              id="image"
              type="file"
              accept="image/*"
              onChange={(e) =>
                setFormData({ ...formData, image_path: e.target.files[0] })
              }
              className="w-full border border-green-300 rounded p-2 bg-white"
              required
            />
          </div>
          <div className="mb-4">
            <label
              htmlFor="plant_date_add"
              className="block text-green-700 font-semibold"
            >
              {labels[language].date}
            </label>
            <input
              id="plant_date_add"
              type="date"
              value={formData.plant_date ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, plant_date: e.target.value })
              }
              className="w-full border border-green-300 rounded p-2"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className={`${submitting ? 'bg-green-300' : 'bg-green-500 hover:bg-green-600'} text-white font-bold py-2 px-4 rounded`}
          >
            {submitting ? 'Adding...' : labels[language].add}
          </button>
        </form>

        <input
          type="text"
          placeholder={labels[language].search}
          value={searchQuery ?? ''}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full border border-green-300 rounded p-2 mb-6"
        />

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => {
              setSortByDate(false);
              fetchAndUpdatePlants(false);
              setMessage({ type: '', text: '' });
            }}
            className={`px-3 py-1 rounded ${
              !sortByDate
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-green-700 hover:bg-gray-300'
            }`}
          >
            {labels[language].defaultOrder}
          </button>
          <button
            onClick={() => {
              setSortByDate(true);
              fetchAndUpdatePlants(true);
              setMessage({ type: '', text: '' });
            }}
            className={`px-3 py-1 rounded ${
              sortByDate
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-green-700 hover:bg-gray-300'
            }`}
          >
            {labels[language].newestFirst}
          </button>
        </div>

        <ul className="space-y-3">
          {filteredPlants.map((plant) => (
            <li
              key={plant.plant_id}
              className="p-4 bg-green-50 border border-green-200 rounded-md shadow-sm flex justify-between items-center"
            >
              <div>
                <div className="font-semibold">
                  {plant[`plant_name_${language}`] ?? '(No name)'}
                </div>
                <div className="italic text-green-600">
                  {plant[`plant_class_${language}`] ?? '(No class)'}
                </div>
                <div className="text-sm text-gray-700">
                  🌐 {plant.botanical_name || '(No botanical name)'}
                </div>
                <div className="text-sm text-gray-700">
                  📍{' '}
                  {language === 'ja' && plant.location_ja
                    ? plant.location_ja
                    : plant.location || '(No location)'}
                </div>
                {plant.plant_date && (
                  <div className="text-sm text-gray-500">
                    {new Date(plant.plant_date).toLocaleDateString()}
                  </div>
                )}
                {plant.image_path && (
                  <img
                    src={`${process.env.REACT_APP_API_URL}/uploads/${plant.image_path}`}
                    alt={plant[`plant_name_${language}`]}
                    className="mt-2 w-32 h-32 object-cover border rounded"
                  />
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEditClick(plant)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
                >
                  {labels[language].edit}
                </button>
                <button
                  onClick={() => handleDelete(plant.plant_id)}
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                >
                  {labels[language].delete}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
      {isModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
        >
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4 text-green-800">
              {labels[language].editModal}
            </h2>

            {['plant_name', 'plant_class'].map((key) =>
              ['en', 'ja'].map((lang) => {
                const isCurrentLang = lang === language;
                return (
                  <div key={`${key}_${lang}`} className="mb-4">
                    <label
                      htmlFor={`${key}_${lang}_edit`}
                      className="block text-green-700 font-semibold"
                    >
                      {
                        labels[language][
                          key === 'plant_name' ? 'name' : 'class'
                        ]
                      }{' '}
                      ({lang.toUpperCase()})
                    </label>
                    <input
                      id={`${key}_${lang}_edit`}
                      type="text"
                      value={editFormData[`${key}_${lang}`] ?? ''}
                      onChange={(e) => {
                        if (isCurrentLang) {
                          setEditFormData({
                            ...editFormData,
                            [`${key}_${lang}`]: e.target.value,
                          });
                        }
                      }}
                      className={`w-full border rounded p-2 ${
                        isCurrentLang
                          ? 'border-green-300'
                          : 'border-gray-300 bg-gray-100 cursor-not-allowed'
                      }`}
                      disabled={!isCurrentLang}
                    />
                  </div>
                );
              })
            )}

            <div className="mb-4">
              <label
                htmlFor="plant_date_edit"
                className="block text-green-700 font-semibold"
              >
                {labels[language].date}
              </label>
              <input
                id="plant_date_edit"
                type="date"
                value={editFormData.plant_date ?? ''}
                onChange={(e) =>
                  setEditFormData({
                    ...editFormData,
                    plant_date: e.target.value,
                  })
                }
                className="w-full border border-green-300 rounded p-2"
              />
            </div>

            <div className="mb-4">
              <label
                htmlFor="botanical_name_edit"
                className="block text-green-700 font-semibold"
              >
                {labels[language].botanical_name}
              </label>
              <input
                id="botanical_name_edit"
                type="text"
                value={editFormData.botanical_name ?? ''}
                onChange={(e) =>
                  setEditFormData({
                    ...editFormData,
                    botanical_name: e.target.value,
                  })
                }
                className="w-full border border-green-300 rounded p-2"
                required
              />
            </div>

            <div className="mb-4">
              <label
                htmlFor="location_edit"
                className="block text-green-700 font-semibold"
              >
                {labels[language].location}
              </label>
              <input
                id="location_edit"
                type="text"
                value={editFormData.location ?? ''}
                onChange={(e) =>
                  setEditFormData({
                    ...editFormData,
                    location: e.target.value,
                  })
                }
                className="w-full border border-green-300 rounded p-2"
                required
              />
            </div>

            <div className="mb-4">
              <label
                htmlFor="image_url_edit"
                className="block text-green-700 font-semibold"
              >
                {labels[language].image_path}
              </label>
              <input
                id="image_url_edit"
                type="url"
                value={editFormData.image_path ?? ''}
                onChange={(e) =>
                  setEditFormData({
                    ...editFormData,
                    image_path: e.target.value,
                  })
                }
                className="w-full border border-green-300 rounded p-2"
                required
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded bg-gray-300 hover:bg-gray-400"
              >
                {labels[language].cancel}
              </button>
              <button
                onClick={handleEditSave}
                className="px-4 py-2 rounded bg-green-600 hover:bg-green-700 text-white"
              >
                {labels[language].save}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
